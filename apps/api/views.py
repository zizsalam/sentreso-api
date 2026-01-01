"""
API utility views.
"""

from rest_framework import views
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.core.cache import cache
from django.db import connection
from django.conf import settings
import redis


class HealthCheckView(views.APIView):
    """Health check endpoint."""
    permission_classes = [AllowAny]

    def get(self, request):
        """Check health of various services."""
        checks = {}
        overall_status = 'healthy'

        # Database check
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                checks['database'] = 'healthy'
        except Exception as e:
            checks['database'] = f'unhealthy: {str(e)}'
            overall_status = 'unhealthy'

        # Redis check
        try:
            redis_url = getattr(settings, 'REDIS_URL', 'redis://localhost:6379/0')
            r = redis.from_url(redis_url)
            r.ping()
            checks['redis'] = 'healthy'
        except Exception as e:
            checks['redis'] = f'unhealthy: {str(e)}'
            overall_status = 'unhealthy'

        # Cache check
        try:
            cache.set('health_check', 'ok', 10)
            if cache.get('health_check') == 'ok':
                checks['cache'] = 'healthy'
            else:
                checks['cache'] = 'unhealthy'
                overall_status = 'unhealthy'
        except Exception as e:
            checks['cache'] = f'unhealthy: {str(e)}'
            overall_status = 'unhealthy'

        return Response({
            'status': overall_status,
            'checks': checks,
        }, status=200 if overall_status == 'healthy' else 503)

