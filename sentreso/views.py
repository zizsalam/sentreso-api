"""
Root view for Sentreso API.
"""

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods


@require_http_methods(["GET"])
def root(request):
    """
    Root endpoint providing API information (JSON for API clients).
    """
    return JsonResponse({
        'name': 'Sentreso Collections & Reconciliation API',
        'version': '1.0.0',
        'description': 'API for payment collections and reconciliation with WhatsApp integration',
        'endpoints': {
            'api_docs': '/api/docs/',
            'api_schema': '/api/schema/',
            'api_v1': '/api/v1/',
            'admin': '/admin/',
            'health': '/api/v1/health/',
        },
        'documentation': 'Visit /api/docs/ for interactive API documentation'
    })


def homepage(request):
    """
    Homepage view - marketing/infra positioning.
    """
    return render(request, 'homepage.html')
