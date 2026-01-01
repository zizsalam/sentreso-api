"""
Reconciliation service for matching payments to collections.
"""

from django.utils import timezone
from decimal import Decimal
from apps.reconciliation.models import PaymentMatch, ReconciliationRecord
from apps.collections.models import Collection
from apps.core.webhooks import send_webhook


class ReconciliationService:
    """Service for reconciling payments with collections."""

    def reconcile(self, master, agent=None):
        """
        Reconcile payments for a master, optionally filtered by agent.

        Args:
            master: Master instance
            agent: Optional Agent instance to filter by

        Returns:
            ReconciliationRecord: The reconciliation record
        """
        # Create reconciliation record
        record = ReconciliationRecord.objects.create(
            master=master,
            agent=agent,
            status='running',
            started_at=timezone.now()
        )

        try:
            # Get unmatched payments
            payments = PaymentMatch.objects.filter(
                master=master,
                is_matched=False
            )
            if agent:
                payments = payments.filter(agent=agent)

            total_payments = payments.count()
            matched_count = 0
            unmatched_count = 0
            total_amount = Decimal('0.00')

            for payment in payments:
                total_amount += payment.amount
                matched = self._match_payment(payment)
                if matched:
                    matched_count += 1
                else:
                    unmatched_count += 1

            # Update record
            record.status = 'completed'
            record.completed_at = timezone.now()
            record.total_payments = total_payments
            record.matched_payments = matched_count
            record.unmatched_payments = unmatched_count
            record.total_amount = total_amount
            record.save()

            return record

        except Exception as e:
            record.status = 'failed'
            record.completed_at = timezone.now()
            record.error_message = str(e)
            record.save()
            return record

    def _match_payment(self, payment):
        """
        Match a payment to a collection.

        Args:
            payment: PaymentMatch instance

        Returns:
            bool: True if payment was matched, False otherwise
        """
        # Find pending collections for this agent
        collections = Collection.objects.filter(
            agent=payment.agent,
            master=payment.master,
            status='pending'
        ).order_by('due_date', 'created_at')

        # Try to match by exact amount first
        for collection in collections:
            if collection.amount == payment.amount:
                # Match found!
                payment.is_matched = True
                payment.matched_collection = collection
                payment.matched_at = timezone.now()
                payment.save()

                # Mark collection as paid
                collection.mark_as_paid(
                    transaction_reference=payment.transaction_reference,
                    payment_method=payment.payment_method,
                    notes=f"Matched via reconciliation: {payment.id}"
                )

                # Send webhook
                send_webhook(
                    master=payment.master,
                    event='collection.paid',
                    data={
                        'collection_id': str(collection.id),
                        'agent_name': collection.agent.name,
                        'amount': str(collection.amount),
                        'status': collection.status,
                        'transaction_reference': payment.transaction_reference,
                        'payment_method': payment.payment_method,
                        'paid_at': collection.paid_at.isoformat() if collection.paid_at else None,
                    }
                )

                return True

        # No exact match found
        return False

