"""
Settings package for Sentreso.

Loads settings based on ENVIRONMENT variable:
- development: development.py
- production: production.py
- testing: testing.py
Default: development
"""

import os

# Use os.environ for initial check to avoid circular import
ENVIRONMENT = os.environ.get('ENVIRONMENT', 'development')

# Now use decouple if available, but fallback to os.environ
try:
    from decouple import config
    ENVIRONMENT = config('ENVIRONMENT', default=ENVIRONMENT)
except ImportError:
    pass

if ENVIRONMENT == 'production':
    from .production import *
elif ENVIRONMENT == 'testing':
    from .testing import *
else:
    from .development import *
