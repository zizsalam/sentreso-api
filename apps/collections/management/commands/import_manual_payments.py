"""
Import manual payments from CSV or generate demo data.

This simulates Wave exports and triggers WhatsApp after each payment.
"""

import csv
from datetime import datetime
from decimal import Decimal
from typing import Iterable

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from apps.masters.models import Master
from apps.collections.services import ManualPaymentRow, PaymentIngestionService


class Command(BaseCommand):
    help = "Import manual payments from CSV or generate demo data for WhatsApp activation."

    def add_arguments(self, parser):
        parser.add_argument("--master-email", required=True, help="Master email to ingest payments for.")
        parser.add_argument("--csv", dest="csv_path", help="Path to CSV file with manual payments.")
        parser.add_argument("--demo", choices=["taxi", "merchant"], help="Generate demo payments.")
        parser.add_argument("--count", type=int, default=10, help="Number of demo payments to generate.")
        parser.add_argument("--phone", help="Force all demo payments to a single phone number.")
        parser.add_argument("--template-name", help="Approved WhatsApp template name to send.")
        parser.add_argument("--template-language", default="fr", help="Template language code (e.g. fr, en_US).")
        parser.add_argument("--message", help="Custom WhatsApp message content (non-template).")
        parser.add_argument("--dry-run", action="store_true", help="Parse and validate only, no writes.")

    def handle(self, *args, **options):
        master = self._get_master(options["master_email"])
        service = PaymentIngestionService(master)

        rows = []
        if options.get("csv_path"):
            rows = list(self._read_csv(options["csv_path"]))
        elif options.get("demo"):
            rows = list(self._generate_demo_rows(options["demo"], options["count"], options.get("phone")))
        else:
            raise CommandError("Provide --csv or --demo.")

        if not rows:
            self.stdout.write(self.style.WARNING("No rows to ingest."))
            return

        if options["dry_run"]:
            self.stdout.write(self.style.SUCCESS(f"Validated {len(rows)} rows (dry run)."))
            return

        results = service.ingest_many(
            rows=rows,
            message=options.get("message"),
            template_name=options.get("template_name"),
            template_language=options.get("template_language"),
        )

        self.stdout.write(self.style.SUCCESS(f"Ingested {len(results)} payments."))
        for res in results[:5]:
            self.stdout.write(
                f"  Collection: {res['collection_id']} | Agent: {res['agent_id']} | "
                f"WhatsApp: {res['whatsapp_status']}"
            )

        if len(results) > 5:
            self.stdout.write("  ...")

    def _get_master(self, email: str) -> Master:
        try:
            return Master.objects.get(email=email)
        except Master.DoesNotExist as exc:
            raise CommandError(f"Master not found: {email}") from exc

    def _read_csv(self, path: str) -> Iterable[ManualPaymentRow]:
        with open(path, newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            required = {"customer_name", "phone_number", "amount", "payment_date", "reference"}
            if not required.issubset(reader.fieldnames or set()):
                raise CommandError(
                    "CSV must contain: customer_name, phone_number, amount, payment_date, reference"
                )

            for row in reader:
                yield ManualPaymentRow(
                    customer_name=row["customer_name"].strip(),
                    phone_number=row["phone_number"].strip(),
                    amount=Decimal(row["amount"]),
                    payment_date=self._parse_date(row["payment_date"]),
                    reference=row["reference"].strip(),
                )

    def _generate_demo_rows(self, scenario: str, count: int, phone_override: str | None) -> Iterable[ManualPaymentRow]:
        now = timezone.now()
        for idx in range(1, count + 1):
            if scenario == "taxi":
                name = f"Taxi Rider {idx}"
                phone = phone_override or f"+221770000{idx:03d}"
                amount = Decimal("2500.00")
                reference = f"WAVE-TAXI-{now:%Y%m%d}-{idx:03d}"
            else:
                name = f"Merchant Customer {idx}"
                phone = phone_override or f"+221780000{idx:03d}"
                amount = Decimal("5000.00")
                reference = f"WAVE-MERCHANT-{now:%Y%m%d}-{idx:03d}"

            yield ManualPaymentRow(
                customer_name=name,
                phone_number=phone,
                amount=amount,
                payment_date=now,
                reference=reference,
            )

    @staticmethod
    def _parse_date(value: str) -> datetime:
        value = value.strip()
        try:
            return datetime.fromisoformat(value)
        except ValueError:
            try:
                return datetime.strptime(value, "%Y-%m-%d")
            except ValueError as exc:
                raise CommandError(f"Invalid payment_date: {value}") from exc


