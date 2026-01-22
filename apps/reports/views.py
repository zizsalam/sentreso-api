"""
API views for Reports and Analytics.
"""

from rest_framework import views, status
from rest_framework.response import Response
from apps.api.permissions import IsAuthenticatedWithAPIKey
from django.db.models import Sum, Count, Avg, Q
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
import csv
from django.http import HttpResponse
from apps.collections.models import Collection
from apps.agents.models import Agent
from apps.reconciliation.models import PaymentMatch
from apps.whatsapp.models import WhatsAppMessage


class DashboardView(views.APIView):
    """View for dashboard statistics."""
    permission_classes = [IsAuthenticatedWithAPIKey]

    def get(self, request):
        """Get dashboard statistics."""
        master = request.master

        # Date range (last 30 days by default)
        days = int(request.query_params.get('days', 30))
        start_date = timezone.now() - timedelta(days=days)

        # Collections statistics
        collections = Collection.objects.filter(master=master, created_at__gte=start_date)
        pending_collections = collections.filter(status='pending')
        paid_collections = collections.filter(status='paid')

        total_collections = collections.count()
        pending_count = pending_collections.count()
        paid_count = paid_collections.count()

        total_amount = collections.aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
        pending_amount = pending_collections.aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
        paid_amount = paid_collections.aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')

        # Calculate recovery rate
        recovery_rate = (paid_amount / total_amount * 100) if total_amount > 0 else Decimal('0.00')

        # Average payment delay
        paid_with_delay = paid_collections.filter(paid_at__isnull=False)
        if paid_with_delay.exists():
            delays = []
            for collection in paid_with_delay:
                if collection.paid_at and collection.created_at:
                    delay = (collection.paid_at - collection.created_at).days
                    delays.append(delay)
            avg_delay = sum(delays) / len(delays) if delays else 0
        else:
            avg_delay = 0

        # Agents statistics
        total_agents = Agent.objects.filter(master=master, is_active=True).count()
        high_risk_agents = Agent.objects.filter(master=master, is_active=True, risk_score__gte=70).count()

        # WhatsApp statistics
        messages = WhatsAppMessage.objects.filter(master=master, created_at__gte=start_date)
        sent_messages = messages.filter(status='sent').count()
        delivered_messages = messages.filter(status='delivered').count()
        read_messages = messages.filter(status='read').count()

        # Payments statistics
        payments = PaymentMatch.objects.filter(master=master, created_at__gte=start_date)
        matched_payments = payments.filter(is_matched=True).count()
        unmatched_payments = payments.filter(is_matched=False).count()

        return Response({
            'period': {
                'days': days,
                'start_date': start_date.isoformat(),
                'end_date': timezone.now().isoformat(),
            },
            'collections': {
                'total': total_collections,
                'pending': pending_count,
                'paid': paid_count,
                'total_amount': str(total_amount),
                'pending_amount': str(pending_amount),
                'paid_amount': str(paid_amount),
                'recovery_rate': float(recovery_rate),
                'avg_payment_delay_days': round(avg_delay, 1),
            },
            'agents': {
                'total': total_agents,
                'high_risk': high_risk_agents,
            },
            'whatsapp': {
                'sent': sent_messages,
                'delivered': delivered_messages,
                'read': read_messages,
            },
            'payments': {
                'matched': matched_payments,
                'unmatched': unmatched_payments,
            },
        })


class CollectionsExportView(views.APIView):
    """View for exporting collections to CSV."""
    permission_classes = [IsAuthenticatedWithAPIKey]

    def get(self, request):
        """Export collections to CSV."""
        master = request.master
        format_type = request.query_params.get('format', 'csv')

        # Build queryset with filters
        queryset = Collection.objects.filter(master=master)

        status_filter = request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        start_date = request.query_params.get('start_date', None)
        if start_date:
            queryset = queryset.filter(created_at__gte=start_date)

        end_date = request.query_params.get('end_date', None)
        if end_date:
            queryset = queryset.filter(created_at__lte=end_date)

        agent_id = request.query_params.get('agent_id', None)
        if agent_id:
            queryset = queryset.filter(agent_id=agent_id)

        # Create CSV response
        response = HttpResponse(content_type='text/csv')
        filename = f"collections_{timezone.now().strftime('%Y-%m-%d')}.csv"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'

        writer = csv.writer(response)
        writer.writerow([
            'ID', 'Agent Name', 'Agent WhatsApp', 'Amount', 'Status',
            'Payment Method', 'Transaction Reference', 'Due Date',
            'Paid At', 'Created At', 'Notes'
        ])

        for collection in queryset:
            writer.writerow([
                str(collection.id),
                collection.agent.name,
                collection.agent.whatsapp_number,
                str(collection.amount),
                collection.status,
                collection.payment_method or '',
                collection.transaction_reference or '',
                collection.due_date.isoformat() if collection.due_date else '',
                collection.paid_at.isoformat() if collection.paid_at else '',
                collection.created_at.isoformat(),
                collection.notes or '',
            ])

        return response





