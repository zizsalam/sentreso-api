"""
Admin UI views for Sentreso.
"""

from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.utils import timezone
from django.conf import settings
from decimal import Decimal
from datetime import datetime
import csv
import io
from apps.masters.models import Master
from apps.collections.models import Collection
from apps.collections.services import ManualPaymentRow, PaymentIngestionService
from apps.whatsapp.models import WhatsAppMessage, WhatsAppTemplate
from apps.whatsapp.services import WhatsAppService
from apps.reconciliation.models import PaymentMatch
from apps.agents.models import Agent


@require_http_methods(["GET", "POST"])
def login(request):
    """
    Admin login using API key.
    """
    if request.method == 'POST':
        api_key = request.POST.get('api_key', '').strip()
        
        if not api_key:
            return render(request, 'admin/login.html', {
                'error': 'API key is required'
            })
        
        try:
            master = Master.objects.get_by_api_key(api_key)
            if not master.is_active:
                return render(request, 'admin/login.html', {
                    'error': 'API key is inactive'
                })
            
            # Store API key in session for API calls
            request.session['api_key'] = api_key
            request.session['master_id'] = str(master.id)
            return redirect('admin_ui:today')
            
        except Master.DoesNotExist:
            return render(request, 'admin/login.html', {
                'error': 'Invalid API key'
            })
    
    # If already logged in, redirect to today
    if 'api_key' in request.session:
        return redirect('admin_ui:today')
    
    return render(request, 'admin/login.html')


@require_http_methods(["GET"])
def today(request):
    """
    Today view - core screen showing collections needing action today.
    """
    if 'api_key' not in request.session:
        return redirect('admin_ui:login')
    
    try:
        api_key = request.session['api_key']
        master = Master.objects.get_by_api_key(api_key)
        
        # Get collections for today (pending status)
        collections_qs = Collection.objects.filter(master=master, status='pending')
        collections = collections_qs.order_by('due_date', 'created_at')[:50]
        overdue_count = collections_qs.filter(due_date__lt=timezone.now()).count()
        
        context = {
            'collections': collections,
            'pending_count': collections_qs.count(),
            'overdue_count': overdue_count,
            'api_key': api_key,  # Pass to template for API calls if needed
        }
        return render(request, 'admin/today.html', context)
    except Master.DoesNotExist:
        request.session.flush()
        return redirect('admin_ui:login')


@require_http_methods(["GET"])
def all_payments(request):
    """
    All payments view - shows all payment matches with filters.
    """
    if 'api_key' not in request.session:
        return redirect('admin_ui:login')
    
    try:
        api_key = request.session['api_key']
        master = Master.objects.get_by_api_key(api_key)
        
        # Get filter parameters
        status_filter = request.GET.get('status', 'all')  # all, matched, unmatched
        payment_method_filter = request.GET.get('method', 'all')
        agent_filter = request.GET.get('agent', '')
        
        # Base queryset
        payments = PaymentMatch.objects.filter(master=master).select_related('agent', 'matched_collection')
        
        # Apply filters
        if status_filter == 'matched':
            payments = payments.filter(is_matched=True)
        elif status_filter == 'unmatched':
            payments = payments.filter(is_matched=False)
        
        if payment_method_filter != 'all':
            payments = payments.filter(payment_method=payment_method_filter)
        
        if agent_filter:
            payments = payments.filter(agent_id=agent_filter)
        
        # Order by received date (newest first)
        payments = payments.order_by('-received_at', '-created_at')[:200]
        
        # Get agents for filter dropdown
        agents_list = Agent.objects.filter(master=master).order_by('name')
        
        context = {
            'payments': payments,
            'total_count': payments.count(),
            'matched_count': PaymentMatch.objects.filter(master=master, is_matched=True).count(),
            'unmatched_count': PaymentMatch.objects.filter(master=master, is_matched=False).count(),
            'status_filter': status_filter,
            'payment_method_filter': payment_method_filter,
            'agent_filter': agent_filter,
            'agents': agents_list,
        }
        return render(request, 'admin/all_payments.html', context)
    except Master.DoesNotExist:
        request.session.flush()
        return redirect('admin_ui:login')


@require_http_methods(["GET"])
def needs_review(request):
    """
    Needs review view - payment reconciliation interface.
    Shows unmatched payments that need to be reviewed and matched to collections.
    """
    if 'api_key' not in request.session:
        return redirect('admin_ui:login')
    
    try:
        api_key = request.session['api_key']
        master = Master.objects.get_by_api_key(api_key)
        
        # Get unmatched payments (is_matched=False)
        unmatched_payments = PaymentMatch.objects.filter(
            master=master,
            is_matched=False
        ).select_related('agent').order_by('-received_at', '-created_at')[:100]
        
        context = {
            'unmatched_payments': unmatched_payments,
            'total_count': unmatched_payments.count(),
        }
        return render(request, 'admin/needs_review.html', context)
    except Master.DoesNotExist:
        request.session.flush()
        return redirect('admin_ui:login')


@require_http_methods(["GET"])
def agents(request):
    """
    Agents management view - list all agents.
    """
    if 'api_key' not in request.session:
        return redirect('admin_ui:login')
    
    try:
        api_key = request.session['api_key']
        master = Master.objects.get_by_api_key(api_key)
        
        # Get all agents for this master
        agents_list = Agent.objects.filter(master=master).order_by('name')
        
        context = {
            'agents': agents_list,
            'total_count': agents_list.count(),
            'active_count': agents_list.filter(is_active=True).count(),
        }
        return render(request, 'admin/agents.html', context)
    except Master.DoesNotExist:
        request.session.flush()
        return redirect('admin_ui:login')


@require_http_methods(["GET"])
def settings(request):
    """
    Settings view - master account settings.
    """
    if 'api_key' not in request.session:
        return redirect('admin_ui:login')
    
    try:
        api_key = request.session['api_key']
        master = Master.objects.get_by_api_key(api_key)
        
        context = {
            'master': master,
            'api_key': api_key,
            'whatsapp_configured': all([
                getattr(settings, 'WHATSAPP_API_URL', None),
                getattr(settings, 'WHATSAPP_API_TOKEN', None),
                getattr(settings, 'WHATSAPP_PHONE_NUMBER_ID', None),
            ]),
            'whatsapp_sender_id': getattr(settings, 'WHATSAPP_PHONE_NUMBER_ID', None),
            'pinpay_template': getattr(settings, 'PINPAY_TEMPLATE_NAME', None),
        }
        return render(request, 'admin/settings.html', context)
    except Master.DoesNotExist:
        request.session.flush()
        return redirect('admin_ui:login')


@require_http_methods(["POST"])
def logout(request):
    """
    Logout from admin.
    """
    request.session.flush()
    return redirect('admin_ui:login')


@require_http_methods(["GET", "POST"])
def manual_import(request):
    """
    Manual CSV import for demo (Wave export simulation).
    """
    if 'api_key' not in request.session:
        return redirect('admin_ui:login')

    api_key = request.session['api_key']
    try:
        master = Master.objects.get_by_api_key(api_key)
    except Master.DoesNotExist:
        request.session.flush()
        return redirect('admin_ui:login')

    context = {
        "preview_rows": [],
        "headers": [],
        "mapping": {},
        "imported": False,
        "errors": [],
        "recent_collections": [],
        "recent_messages": [],
        "summary": None,
        "campaign_summary": None,
        "failed_messages": [],
    }

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "preview":
            upload = request.FILES.get("csv_file")
            if not upload:
                context["errors"].append("CSV file is required.")
            else:
                try:
                    decoded = upload.read().decode("utf-8-sig")
                    reader = csv.DictReader(io.StringIO(decoded))
                    headers = reader.fieldnames or []
                    rows = [row for row in reader]
                except Exception as exc:
                    context["errors"].append(f"Failed to parse CSV: {exc}")
                    headers = []
                    rows = []

                if len(rows) > 500:
                    context["errors"].append(
                        "CSV too large for UI preview. Use the CLI import for large files."
                    )

                request.session["manual_import_headers"] = headers
                request.session["manual_import_rows"] = rows

                context["headers"] = headers
                context["preview_rows"] = rows[:10]
                context["mapping"] = _suggest_mapping(headers)

        elif action == "import":
            headers = request.session.get("manual_import_headers", [])
            rows = request.session.get("manual_import_rows", [])
            if not rows or not headers:
                context["errors"].append("No preview data found. Please upload CSV first.")
            else:
                if request.POST.get("confirm_send") != "yes":
                    context["errors"].append(
                        "Please confirm you understand messages will be sent immediately."
                    )
                    context["headers"] = headers
                    context["preview_rows"] = rows[:10]
                    context["mapping"] = _suggest_mapping(headers)
                    return render(request, "admin/manual_import.html", context)

                mapping = {
                    "customer_name": request.POST.get("map_customer_name", "").strip(),
                    "phone_number": request.POST.get("map_phone_number", "").strip(),
                    "amount": request.POST.get("map_amount", "").strip(),
                    "payment_date": request.POST.get("map_payment_date", "").strip(),
                    "reference": request.POST.get("map_reference", "").strip(),
                }

                missing = [k for k, v in mapping.items() if not v]
                if missing:
                    context["errors"].append(
                        "Missing column mapping: " + ", ".join(missing)
                    )
                    context["headers"] = headers
                    context["preview_rows"] = rows[:10]
                    context["mapping"] = mapping
                else:
                    parsed_rows = []
                    for row in rows:
                        parsed_rows.append(
                            ManualPaymentRow(
                                customer_name=row.get(mapping["customer_name"], "").strip(),
                                phone_number=row.get(mapping["phone_number"], "").strip(),
                                amount=_parse_amount(row.get(mapping["amount"], "")),
                                payment_date=_parse_date(row.get(mapping["payment_date"], "")),
                                reference=row.get(mapping["reference"], "").strip(),
                            )
                        )

                    service = PaymentIngestionService(master)
                    results = service.ingest_many(
                        rows=parsed_rows,
                        message=request.POST.get("message") or None,
                        template_name=request.POST.get("template_name") or None,
                        template_language=request.POST.get("template_language") or "fr",
                    )
                    context["imported"] = True
                    context["summary"] = _build_summary(results)
                    request.session["manual_import_collection_ids"] = [
                        r.get("collection_id") for r in results if r.get("collection_id")
                    ]
                    request.session.pop("manual_import_headers", None)
                    request.session.pop("manual_import_rows", None)
        elif action == "generate":
            scenario = request.POST.get("scenario", "taxi")
            count = int(request.POST.get("count") or 10)
            rows = list(_generate_demo_rows(scenario, count, request.POST.get("phone")))
            service = PaymentIngestionService(master)
            results = service.ingest_many(
                rows=rows,
                message=request.POST.get("message") or None,
                template_name=request.POST.get("template_name") or None,
                template_language=request.POST.get("template_language") or "fr",
            )
            context["imported"] = True
            context["summary"] = _build_summary(results)
            request.session["manual_import_collection_ids"] = [
                r.get("collection_id") for r in results if r.get("collection_id")
            ]
        elif action == "campaign_last_import":
            collection_ids = request.session.get("manual_import_collection_ids", [])
            context["campaign_summary"] = _run_campaign(
                master=master,
                collection_ids=collection_ids,
                label="last import",
            )
        elif action == "campaign_today":
            today = timezone.localdate()
            collections = Collection.objects.filter(
                master=master,
                status="paid",
                paid_at__date=today,
            )
            context["campaign_summary"] = _run_campaign(
                master=master,
                collection_ids=[str(c.id) for c in collections],
                label="today's payers",
            )

    # Live audit panel
    context["recent_collections"] = (
        Collection.objects.filter(master=master).order_by("-created_at")[:10]
    )
    context["recent_messages"] = (
        WhatsAppMessage.objects.filter(master=master).order_by("-created_at")[:10]
    )
    context["failed_messages"] = (
        WhatsAppMessage.objects.filter(master=master, status="failed")
        .order_by("-created_at")[:5]
    )
    context["master"] = master
    context["sender_id"] = getattr(settings, "WHATSAPP_PHONE_NUMBER_ID", None)
    context["pinpay_template"] = getattr(settings, "PINPAY_TEMPLATE_NAME", None) or "pinpay"
    context["pinpay_language"] = getattr(settings, "PINPAY_TEMPLATE_LANGUAGE", "fr")
    context["last_import_count"] = len(request.session.get("manual_import_collection_ids", []))

    return render(request, "admin/manual_import.html", context)


@require_http_methods(["GET"])
def collection_detail(request, collection_id):
    if 'api_key' not in request.session:
        return redirect('admin_ui:login')

    api_key = request.session['api_key']
    try:
        master = Master.objects.get_by_api_key(api_key)
        collection = Collection.objects.get(id=collection_id, master=master)
        messages = WhatsAppMessage.objects.filter(collection=collection).order_by('-created_at')[:10]
        context = {
            'collection': collection,
            'messages': messages,
        }
        return render(request, 'admin/collection_detail.html', context)
    except (Master.DoesNotExist, Collection.DoesNotExist):
        request.session.flush()
        return redirect('admin_ui:login')


@require_http_methods(["GET"])
def payment_detail(request, payment_id):
    if 'api_key' not in request.session:
        return redirect('admin_ui:login')

    api_key = request.session['api_key']
    try:
        master = Master.objects.get_by_api_key(api_key)
        payment = PaymentMatch.objects.get(id=payment_id, master=master)
        context = {
            'payment': payment,
            'matched_collection': payment.matched_collection,
        }
        return render(request, 'admin/payment_detail.html', context)
    except (Master.DoesNotExist, PaymentMatch.DoesNotExist):
        request.session.flush()
        return redirect('admin_ui:login')


@require_http_methods(["GET"])
def agent_detail(request, agent_id):
    if 'api_key' not in request.session:
        return redirect('admin_ui:login')


@require_http_methods(["GET", "POST"])
def whatsapp_compose(request):
    """
    Simple WhatsApp composer for demo (template or custom).
    """
    if 'api_key' not in request.session:
        return redirect('admin_ui:login')

    api_key = request.session['api_key']
    try:
        master = Master.objects.get_by_api_key(api_key)
    except Master.DoesNotExist:
        request.session.flush()
        return redirect('admin_ui:login')

    agents = Agent.objects.filter(master=master).order_by('name')
    templates = WhatsAppTemplate.objects.filter(
        master=master,
        whatsapp_template_name__isnull=False
    ).order_by('name')

    context = {
        "agents": agents,
        "templates": templates,
        "recent_messages": WhatsAppMessage.objects.filter(master=master).order_by('-created_at')[:10],
        "success": None,
        "error": None,
    }

    if request.method == "POST":
        agent_id = request.POST.get("agent_id")
        template_id = request.POST.get("template_id")
        custom_message = (request.POST.get("message") or "").strip()
        param_1 = (request.POST.get("param_1") or "").strip()
        param_2 = (request.POST.get("param_2") or "").strip()
        param_3 = (request.POST.get("param_3") or "").strip()
        param_4 = (request.POST.get("param_4") or "").strip()

        try:
            agent = Agent.objects.get(id=agent_id, master=master)
        except Agent.DoesNotExist:
            context["error"] = "Agent not found."
            return render(request, "admin/whatsapp_compose.html", context)

        template = None
        metadata = {}
        if template_id:
            try:
                template = WhatsAppTemplate.objects.get(id=template_id, master=master)
            except WhatsAppTemplate.DoesNotExist:
                context["error"] = "Template not found."
                return render(request, "admin/whatsapp_compose.html", context)

            params = [p for p in [param_1, param_2, param_3, param_4] if p]
            metadata = {"template_params": params}

        if not template and not custom_message:
            context["error"] = "Provide a template or a custom message."
            return render(request, "admin/whatsapp_compose.html", context)

        message = WhatsAppMessage.objects.create(
            master=master,
            agent=agent,
            template=template,
            direction="outbound",
            status="pending",
            to_number=agent.whatsapp_number,
            content=custom_message or f"Template: {template.whatsapp_template_name}",
            metadata=metadata,
        )

        service = WhatsAppService()
        success = service.send_message(message)
        if success:
            message.status = "sent"
            message.sent_at = timezone.now()
            message.save()
            context["success"] = "Message sent."
        else:
            message.status = "failed"
            message.save()
            context["error"] = message.error_message or "Message failed."

        context["recent_messages"] = WhatsAppMessage.objects.filter(master=master).order_by('-created_at')[:10]

    return render(request, "admin/whatsapp_compose.html", context)

    api_key = request.session['api_key']
    try:
        master = Master.objects.get_by_api_key(api_key)
        agent = Agent.objects.get(id=agent_id, master=master)
        collections = Collection.objects.filter(agent=agent).order_by('-created_at')[:10]
        messages = WhatsAppMessage.objects.filter(agent=agent).order_by('-created_at')[:10]
        context = {
            'agent': agent,
            'collections': collections,
            'messages': messages,
        }
        return render(request, 'admin/agent_detail.html', context)
    except (Master.DoesNotExist, Agent.DoesNotExist):
        request.session.flush()
        return redirect('admin_ui:login')


def _suggest_mapping(headers):
    lower = {h.lower(): h for h in headers}
    def pick(*names):
        for name in names:
            if name in lower:
                return lower[name]
        return ""

    return {
        "customer_name": pick("customer_name", "customer", "name", "nom", "client"),
        "phone_number": pick("phone_number", "whatsapp", "phone", "telephone", "numero"),
        "amount": pick("amount", "montant"),
        "payment_date": pick("payment_date", "date", "horodatage", "timestamp"),
        "reference": pick("reference", "transaction", "identifiant", "transaction_id"),
    }


def _parse_amount(value):
    raw = (value or "").strip().replace(" ", "")
    if raw.count(",") == 1 and raw.count(".") == 0:
        raw = raw.replace(",", ".")
    return Decimal(raw or "0")


def _parse_date(value):
    raw = (value or "").strip()
    if not raw:
        return timezone.now()
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(raw, fmt)
        except ValueError:
            continue
    try:
        return datetime.fromisoformat(raw)
    except ValueError:
        return timezone.now()


def _build_summary(results):
    if not results:
        return None
    agent_ids = {r.get("agent_id") for r in results if r.get("agent_id")}
    sent = 0
    failed = 0
    skipped = 0
    for r in results:
        status = r.get("whatsapp_status")
        if status == "sent":
            sent += 1
        elif status == "failed":
            failed += 1
        else:
            skipped += 1
    return {
        "payments": len(results),
        "agents": len(agent_ids),
        "sent": sent,
        "failed": failed,
        "skipped": skipped,
    }


def _get_pinpay_template(master):
    template_name = getattr(settings, "PINPAY_TEMPLATE_NAME", None)
    template_language = getattr(settings, "PINPAY_TEMPLATE_LANGUAGE", "fr")
    if not template_name:
        return None
    template, _ = WhatsAppTemplate.objects.get_or_create(
        master=master,
        whatsapp_template_name=template_name,
        defaults={
            "name": f"Pinpay Template {template_name}",
            "template_type": "custom",
            "content": f"Template: {template_name}",
            "language_code": template_language,
            "is_active": True,
        },
    )
    return template


def _run_campaign(master, collection_ids, label):
    if not collection_ids:
        return {"error": f"No collections found for {label}."}

    template = _get_pinpay_template(master)
    if not template:
        return {"error": "PINPAY_TEMPLATE_NAME is not configured."}

    collections = Collection.objects.filter(master=master, id__in=collection_ids)
    if not collections:
        return {"error": f"No collections found for {label}."}

    service = WhatsAppService()
    sent = 0
    failed = 0
    for collection in collections:
        agent = collection.agent
        amount = str(collection.amount)
        currency = "XOF"
        reference = collection.transaction_reference or "-"
        timestamp = (
            collection.paid_at.strftime("%Y-%m-%d %H:%M:%S")
            if collection.paid_at
            else collection.created_at.strftime("%Y-%m-%d %H:%M:%S")
        )

        message = WhatsAppMessage.objects.create(
            master=master,
            agent=agent,
            collection=collection,
            template=template,
            direction="outbound",
            status="pending",
            to_number=agent.whatsapp_number,
            content=f"Template: {template.whatsapp_template_name}",
            metadata={
                "template_params": [amount, currency, reference, timestamp],
            },
        )

        success = service.send_message(message)
        if success:
            message.status = "sent"
            message.sent_at = timezone.now()
            sent += 1
        else:
            message.status = "failed"
            failed += 1
        message.save()

    return {
        "label": label,
        "sent": sent,
        "failed": failed,
        "total": sent + failed,
    }


def _generate_demo_rows(scenario: str, count: int, phone_override: str | None):
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

