"""
Manual payment ingestion service for demo flows.

This service simulates Wave exports by creating paid Collections and
immediately triggering WhatsApp messages. It keeps everything auditable
in the database while remaining manual and demo-friendly.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Iterable, Optional

from django.utils import timezone

from apps.agents.models import Agent
from apps.collections.models import Collection
from apps.masters.models import Master
from apps.reconciliation.models import PaymentMatch
from apps.whatsapp.models import WhatsAppMessage, WhatsAppTemplate
from apps.whatsapp.services import WhatsAppService
from django.conf import settings


@dataclass
class ManualPaymentRow:
    customer_name: str
    phone_number: str
    amount: Decimal
    payment_date: datetime
    reference: str


class PaymentIngestionService:
    """
    Ingests manual payments and triggers WhatsApp.

    Manual -> automated transition:
    - Manual source (CSV/seed) provides already-paid transactions.
    - We persist them as paid Collections for auditability.
    - We trigger WhatsApp immediately (template or custom).
    """

    def __init__(self, master: Master):
        self.master = master
        self.whatsapp_service = WhatsAppService()

    def ingest_payment(
        self,
        row: ManualPaymentRow,
        message: Optional[str] = None,
        template_name: Optional[str] = None,
        template_language: str = "fr",
    ) -> dict:
        agent = self._get_or_create_agent(row.customer_name, row.phone_number)
        collection = self._create_paid_collection(agent, row)
        self._create_payment_match(agent, collection, row)

        whatsapp_message = self._trigger_whatsapp(
            agent=agent,
            collection=collection,
            message=message,
            template_name=template_name,
            template_language=template_language,
        )

        return {
            "collection_id": str(collection.id),
            "agent_id": str(agent.id),
            "whatsapp_message_id": str(whatsapp_message.id) if whatsapp_message else None,
            "whatsapp_status": whatsapp_message.status if whatsapp_message else None,
        }

    def ingest_many(
        self,
        rows: Iterable[ManualPaymentRow],
        message: Optional[str] = None,
        template_name: Optional[str] = None,
        template_language: str = "fr",
    ) -> list[dict]:
        results = []
        for row in rows:
            results.append(
                self.ingest_payment(
                    row=row,
                    message=message,
                    template_name=template_name,
                    template_language=template_language,
                )
            )
        return results

    def _get_or_create_agent(self, name: str, phone_number: str) -> Agent:
        normalized = self._normalize_phone(phone_number)
        agent, _ = Agent.objects.get_or_create(
            master=self.master,
            whatsapp_number=normalized,
            defaults={
                "name": name,
                "phone_number": normalized,
                "is_active": True,
            },
        )
        if agent.name != name:
            agent.name = name
            agent.save(update_fields=["name"])
        return agent

    def _create_paid_collection(self, agent: Agent, row: ManualPaymentRow) -> Collection:
        notes = (
            "Manual Wave import (demo).\n"
            f"Customer: {row.customer_name}\n"
            f"Phone: {self._normalize_phone(row.phone_number)}\n"
            f"Reference: {row.reference}\n"
            f"Payment Date: {row.payment_date.isoformat()}\n"
        )
        collection = Collection.objects.create(
            master=self.master,
            agent=agent,
            amount=row.amount,
            status="paid",
            payment_method="mobile_money",
            transaction_reference=row.reference,
            due_date=row.payment_date,
            paid_at=row.payment_date,
            notes=notes,
        )
        return collection

    def _create_payment_match(self, agent: Agent, collection: Collection, row: ManualPaymentRow) -> None:
        """
        Record the received payment in PaymentMatch for auditability.
        """
        PaymentMatch.objects.update_or_create(
            master=self.master,
            transaction_reference=row.reference,
            defaults={
                "agent": agent,
                "amount": row.amount,
                "payment_method": "mobile_money",
                "received_at": row.payment_date,
                "is_matched": True,
                "matched_collection": collection,
                "matched_at": timezone.now(),
                "notes": "Manual Wave import (demo).",
            },
        )

    def _trigger_whatsapp(
        self,
        agent: Agent,
        collection: Collection,
        message: Optional[str],
        template_name: Optional[str],
        template_language: str,
    ) -> Optional[WhatsAppMessage]:
        if not message and not template_name:
            return None

        template_obj = None
        metadata = {}
        if template_name:
            # Resolve logical alias (e.g., "pinpay") to approved template name
            resolved_name, resolved_language = self._resolve_template_alias(
                template_name, template_language
            )
            template_obj = WhatsAppTemplate.objects.filter(
                master=self.master,
                whatsapp_template_name=resolved_name,
                is_active=True,
            ).first()
            if not template_obj:
                template_obj = WhatsAppTemplate.objects.create(
                    master=self.master,
                    name=f"Manual Template: {resolved_name}",
                    whatsapp_template_name=resolved_name,
                    template_type="custom",
                    content=f"Template: {resolved_name}",
                    language_code=resolved_language,
                    is_active=True,
                )
            metadata = {
                "template_used": resolved_name,
                "template_params": {
                    "agent_name": agent.name,
                    "amount": str(collection.amount),
                    "due_date": collection.paid_at.strftime("%Y-%m-%d") if collection.paid_at else "",
                },
            }

        content = message or f"Paiement recu: {collection.amount} FCFA. Merci {agent.name}."
        whatsapp_message = WhatsAppMessage.objects.create(
            master=self.master,
            agent=agent,
            collection=collection,
            template=template_obj,
            direction="outbound",
            status="pending",
            to_number=agent.whatsapp_number,
            content=content,
            metadata=metadata,
        )

        success = self.whatsapp_service.send_message(whatsapp_message)
        if success:
            whatsapp_message.status = "sent"
            whatsapp_message.sent_at = timezone.now()
        else:
            whatsapp_message.status = "failed"
        whatsapp_message.save()
        return whatsapp_message

    @staticmethod
    def _resolve_template_alias(
        template_name: str,
        template_language: str,
    ) -> tuple[str, str]:
        if template_name.lower() == "pinpay":
            resolved_name = getattr(settings, "PINPAY_TEMPLATE_NAME", None)
            resolved_language = getattr(settings, "PINPAY_TEMPLATE_LANGUAGE", template_language)
            if resolved_name:
                return resolved_name, resolved_language
        return template_name, template_language

    @staticmethod
    def _normalize_phone(phone_number: str) -> str:
        normalized = phone_number.strip()
        if normalized.startswith("00"):
            normalized = "+" + normalized[2:]
        if not normalized.startswith("+"):
            normalized = "+" + normalized
        return normalized

