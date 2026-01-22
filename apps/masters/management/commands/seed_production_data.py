"""
Seed production data for testing Pinpay with real WhatsApp numbers.

Creates two use cases:
1. Merchant Activation (Loyalty) - Retail chain tracking customer payments
2. Village Enterprise / Agent Networks (myAgro-style) - NGO tracking VE payments

Test users:
- Abdoul Aziz KANE: +221774454330 (WhatsApp verified)
- Maryam KANE: +221774187030 (WhatsApp verified)

Usage:
    python manage.py seed_production_data
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from apps.masters.models import Master
from apps.agents.models import Agent
from apps.collections.models import Collection
from apps.whatsapp.models import WhatsAppTemplate


class Command(BaseCommand):
    help = 'Seed production data for testing Pinpay with real WhatsApp numbers'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing seed data before creating new data',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Starting production seed data creation...'))
        
        if options['clear']:
            self.clear_seed_data()
        
        # Create Use Case 1: Merchant Activation (Loyalty)
        self.stdout.write(self.style.NOTICE('\n=== USE CASE 1: Merchant Activation (Loyalty) ==='))
        loyalty_master = self.create_loyalty_use_case()
        
        # Create Use Case 2: Village Enterprise / Agent Networks (myAgro-style)
        self.stdout.write(self.style.NOTICE('\n=== USE CASE 2: Village Enterprise / Agent Networks ==='))
        myagro_master = self.create_myagro_use_case()
        
        self.stdout.write(self.style.SUCCESS('\n=== SEED DATA CREATED SUCCESSFULLY ==='))
        self.print_summary(loyalty_master, myagro_master)

    def clear_seed_data(self):
        """Clear existing seed data."""
        self.stdout.write(self.style.WARNING('Clearing existing seed data...'))
        
        # Delete masters created by this script (by email pattern)
        Master.objects.filter(email__in=[
            'loyalty@pinpay-test.com',
            'myagro@pinpay-test.com'
        ]).delete()
        
        self.stdout.write(self.style.SUCCESS('Seed data cleared.'))

    def create_loyalty_use_case(self):
        """
        Create Merchant Activation (Loyalty) use case.
        
        Scenario: A retail chain (Chez Fatou) tracks customer payments 
        and rewards repeat visits with loyalty points.
        """
        # Create Master (Retail Chain)
        master, created = Master.objects.get_or_create(
            email='loyalty@pinpay-test.com',
            defaults={
                'name': 'Chez Fatou - Boutique Dakar',
                'webhook_url': 'https://webhook.site/pinpay-loyalty-test',
                'is_active': True,
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created Master: {master.name}'))
            self.stdout.write(f'  API Key: {master.api_key}')
        else:
            self.stdout.write(f'Master already exists: {master.name}')
            self.stdout.write(f'  API Key: {master.api_key}')
        
        # Create Agent (Customer - Abdoul Aziz)
        customer_aziz, created = Agent.objects.get_or_create(
            master=master,
            whatsapp_number='+221774454330',
            defaults={
                'name': 'Abdoul Aziz KANE',
                'phone_number': '+221774454330',
                'risk_score': Decimal('10.0'),  # Low risk - good customer
                'is_active': True,
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created Customer: {customer_aziz.name}'))
        else:
            self.stdout.write(f'Customer already exists: {customer_aziz.name}')
        
        # Create WhatsApp Templates for Loyalty
        templates_data = [
            {
                'name': 'Loyalty Welcome',
                'template_type': 'custom',
                'content': 'Bienvenue chez Fatou, {customer_name}! Merci pour votre achat de {amount} FCFA. Vous avez gagne {points} points de fidelite. Total: {total_points} points.',
                'variables': {'customer_name': 'Nom du client', 'amount': 'Montant', 'points': 'Points gagnes', 'total_points': 'Total points'},
                'language_code': 'fr',
            },
            {
                'name': 'Loyalty Reminder',
                'template_type': 'collection_reminder',
                'content': 'Bonjour {customer_name}! Vous avez {total_points} points chez Fatou. Passez nous voir pour les utiliser! Promo: -10% sur votre prochain achat.',
                'variables': {'customer_name': 'Nom du client', 'total_points': 'Total points'},
                'language_code': 'fr',
            },
            {
                'name': 'Payment Confirmation Loyalty',
                'template_type': 'payment_confirmation',
                'content': 'Merci {customer_name}! Paiement de {amount} FCFA recu. +{points} points! Votre solde: {total_points} points. A bientot chez Fatou!',
                'variables': {'customer_name': 'Nom du client', 'amount': 'Montant', 'points': 'Points', 'total_points': 'Total'},
                'language_code': 'fr',
            },
        ]
        
        for tpl_data in templates_data:
            tpl, created = WhatsAppTemplate.objects.get_or_create(
                master=master,
                name=tpl_data['name'],
                defaults=tpl_data
            )
            if created:
                self.stdout.write(f'  Created Template: {tpl.name}')
        
        # Create Collections (Customer purchases/visits)
        now = timezone.now()
        collections_data = [
            {
                'agent': customer_aziz,
                'amount': Decimal('15000.00'),
                'status': 'paid',
                'payment_method': 'mobile_money',
                'transaction_reference': 'WAVE20241228001',
                'due_date': now - timedelta(days=7),
                'paid_at': now - timedelta(days=7),
                'notes': 'Achat: Riz 25kg, Huile 5L. Points: 150. Client fidele.',
            },
            {
                'agent': customer_aziz,
                'amount': Decimal('8500.00'),
                'status': 'paid',
                'payment_method': 'cash',
                'transaction_reference': 'CASH20241230001',
                'due_date': now - timedelta(days=5),
                'paid_at': now - timedelta(days=5),
                'notes': 'Achat: Lait, Sucre, Cafe. Points: 85. Visite reguliere.',
            },
            {
                'agent': customer_aziz,
                'amount': Decimal('25000.00'),
                'status': 'pending',
                'due_date': now + timedelta(days=3),
                'notes': 'Commande speciale: Provisions fete. Points potentiels: 250. Rappel WhatsApp a envoyer.',
            },
        ]
        
        for coll_data in collections_data:
            coll, created = Collection.objects.get_or_create(
                master=master,
                agent=coll_data['agent'],
                amount=coll_data['amount'],
                due_date=coll_data['due_date'],
                defaults=coll_data
            )
            if created:
                self.stdout.write(f'  Created Collection: {coll.amount} FCFA - {coll.status}')
        
        return master

    def create_myagro_use_case(self):
        """
        Create Village Enterprise / Agent Networks (myAgro-style) use case.
        
        Scenario: An NGO (Semences Sahel) works with Village Entrepreneurs (VEs)
        who collect payments from farmers for agricultural inputs.
        """
        # Create Master (NGO)
        master, created = Master.objects.get_or_create(
            email='myagro@pinpay-test.com',
            defaults={
                'name': 'Semences Sahel - Programme Agricole',
                'webhook_url': 'https://webhook.site/pinpay-myagro-test',
                'is_active': True,
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created Master: {master.name}'))
            self.stdout.write(f'  API Key: {master.api_key}')
        else:
            self.stdout.write(f'Master already exists: {master.name}')
            self.stdout.write(f'  API Key: {master.api_key}')
        
        # Create Agent (Village Entrepreneur - Maryam)
        ve_maryam, created = Agent.objects.get_or_create(
            master=master,
            whatsapp_number='+221774187030',
            defaults={
                'name': 'Maryam KANE',
                'phone_number': '+221774187030',
                'risk_score': Decimal('5.0'),  # Very low risk - trusted VE
                'is_active': True,
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created VE: {ve_maryam.name}'))
        else:
            self.stdout.write(f'VE already exists: {ve_maryam.name}')
        
        # Create WhatsApp Templates for myAgro-style
        templates_data = [
            {
                'name': 'VE Payment Reminder',
                'template_type': 'collection_reminder',
                'content': 'Bonjour {ve_name}! Rappel: Vous devez verser {amount} FCFA pour les paiements agriculteurs de {village}. Echeance: {due_date}. Merci pour votre travail!',
                'variables': {'ve_name': 'Nom VE', 'amount': 'Montant', 'village': 'Village', 'due_date': 'Date echeance'},
                'language_code': 'fr',
            },
            {
                'name': 'VE Payment Confirmation',
                'template_type': 'payment_confirmation',
                'content': 'Merci {ve_name}! Versement de {amount} FCFA recu pour {village}. Agriculteurs credites: {farmer_count}. Solde restant: {remaining} FCFA.',
                'variables': {'ve_name': 'Nom VE', 'amount': 'Montant', 'village': 'Village', 'farmer_count': 'Nb agriculteurs', 'remaining': 'Restant'},
                'language_code': 'fr',
            },
            {
                'name': 'Farmer Registration Confirmation',
                'template_type': 'custom',
                'content': 'Nouveau agriculteur inscrit! {farmer_name} de {village} - Cycle: {cycle}. Montant total: {amount} FCFA. Merci {ve_name}!',
                'variables': {'farmer_name': 'Nom agriculteur', 'village': 'Village', 'cycle': 'Cycle', 'amount': 'Montant', 've_name': 'Nom VE'},
                'language_code': 'fr',
            },
            {
                'name': 'Weekly Summary',
                'template_type': 'custom',
                'content': 'Resume semaine - {ve_name}:\n- Agriculteurs: {farmer_count}\n- Collecte: {collected} FCFA\n- Objectif: {target} FCFA\n- Taux: {rate}%\nBravo!',
                'variables': {'ve_name': 'Nom VE', 'farmer_count': 'Nb agriculteurs', 'collected': 'Collecte', 'target': 'Objectif', 'rate': 'Taux'},
                'language_code': 'fr',
            },
        ]
        
        for tpl_data in templates_data:
            tpl, created = WhatsAppTemplate.objects.get_or_create(
                master=master,
                name=tpl_data['name'],
                defaults=tpl_data
            )
            if created:
                self.stdout.write(f'  Created Template: {tpl.name}')
        
        # Create Collections (Farmer payments collected by VE)
        now = timezone.now()
        collections_data = [
            # Paid collections - successful farmer payments
            {
                'agent': ve_maryam,
                'amount': Decimal('45000.00'),
                'status': 'paid',
                'payment_method': 'mobile_money',
                'transaction_reference': 'OM20241220001',
                'due_date': now - timedelta(days=14),
                'paid_at': now - timedelta(days=14),
                'notes': 'Village: Thies-Nord | Agriculteurs: Amadou Diallo (15000), Fatou Ndiaye (15000), Ibrahima Sow (15000) | Cycle: Hivernage 2024 | Intrants: Semences mil + engrais',
            },
            {
                'agent': ve_maryam,
                'amount': Decimal('30000.00'),
                'status': 'paid',
                'payment_method': 'cash',
                'transaction_reference': 'CASH20241225001',
                'due_date': now - timedelta(days=10),
                'paid_at': now - timedelta(days=9),
                'notes': 'Village: Thies-Nord | Agriculteurs: Moussa Ba (10000), Aissatou Fall (10000), Omar Diop (10000) | Cycle: Hivernage 2024 | Intrants: Semences arachide',
            },
            # Pending collection - due soon
            {
                'agent': ve_maryam,
                'amount': Decimal('60000.00'),
                'status': 'pending',
                'due_date': now + timedelta(days=2),
                'notes': 'Village: Thies-Nord | Agriculteurs en attente: Cheikh Niang (20000), Mariama Sy (20000), Abdoulaye Gueye (20000) | Cycle: Contre-saison 2025 | Intrants: Semences maraicheres + irrigation',
            },
            # Pending collection - overdue (for testing reminders)
            {
                'agent': ve_maryam,
                'amount': Decimal('25000.00'),
                'status': 'pending',
                'due_date': now - timedelta(days=3),
                'notes': 'Village: Mbour-Est | Agriculteurs: Ousmane Faye (12500), Khady Mbaye (12500) | Cycle: Hivernage 2024 | RETARD - Rappel WhatsApp necessaire',
            },
        ]
        
        for coll_data in collections_data:
            coll, created = Collection.objects.get_or_create(
                master=master,
                agent=coll_data['agent'],
                amount=coll_data['amount'],
                due_date=coll_data['due_date'],
                defaults=coll_data
            )
            if created:
                status_display = 'OVERDUE' if coll.is_overdue() else coll.status.upper()
                self.stdout.write(f'  Created Collection: {coll.amount} FCFA - {status_display}')
        
        return master

    def print_summary(self, loyalty_master, myagro_master):
        """Print summary of created data."""
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('PRODUCTION SEED DATA SUMMARY'))
        self.stdout.write('='*60)
        
        self.stdout.write(self.style.NOTICE('\n--- USE CASE 1: Merchant Activation (Loyalty) ---'))
        self.stdout.write(f'Master: {loyalty_master.name}')
        self.stdout.write(f'Email: {loyalty_master.email}')
        self.stdout.write(self.style.WARNING(f'API Key: {loyalty_master.api_key}'))
        self.stdout.write(f'Agents: {loyalty_master.agents.count()}')
        self.stdout.write(f'Collections: {loyalty_master.collections.count()}')
        self.stdout.write(f'Templates: {loyalty_master.whatsapp_templates.count()}')
        
        self.stdout.write(self.style.NOTICE('\n--- USE CASE 2: Village Enterprise (myAgro-style) ---'))
        self.stdout.write(f'Master: {myagro_master.name}')
        self.stdout.write(f'Email: {myagro_master.email}')
        self.stdout.write(self.style.WARNING(f'API Key: {myagro_master.api_key}'))
        self.stdout.write(f'Agents: {myagro_master.agents.count()}')
        self.stdout.write(f'Collections: {myagro_master.collections.count()}')
        self.stdout.write(f'Templates: {myagro_master.whatsapp_templates.count()}')
        
        self.stdout.write(self.style.NOTICE('\n--- TEST WHATSAPP NUMBERS ---'))
        self.stdout.write('Abdoul Aziz KANE: +221774454330 (Loyalty Customer)')
        self.stdout.write('Maryam KANE: +221774187030 (Village Entrepreneur)')
        
        self.stdout.write(self.style.NOTICE('\n--- NEXT STEPS ---'))
        self.stdout.write('1. Test WhatsApp flow with:')
        self.stdout.write('   curl -X POST https://api.pinpay.com/v1/whatsapp/send/ \\')
        self.stdout.write(f'     -H "Authorization: Bearer {loyalty_master.api_key}" \\')
        self.stdout.write('     -H "Content-Type: application/json" \\')
        self.stdout.write('     -d \'{"to_number": "+221774454330", "template_name": "Loyalty Welcome", "variables": {"customer_name": "Abdoul Aziz", "amount": "15000", "points": "150", "total_points": "235"}}\'')
        self.stdout.write('')
        self.stdout.write('2. Check pending collections:')
        self.stdout.write(f'   curl -H "Authorization: Bearer {myagro_master.api_key}" \\')
        self.stdout.write('     https://api.pinpay.com/v1/collections/?status=pending')
        self.stdout.write('')
        self.stdout.write('3. Send reminder for overdue collection:')
        self.stdout.write(f'   curl -X POST https://api.pinpay.com/v1/whatsapp/send-reminder/<collection_id>/ \\')
        self.stdout.write(f'     -H "Authorization: Bearer {myagro_master.api_key}"')
        
        self.stdout.write('\n' + '='*60)

