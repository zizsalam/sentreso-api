"""
Custom exceptions for Sentreso API.
"""

from rest_framework.exceptions import APIException


class ValidationError(APIException):
    """Custom validation error."""
    status_code = 400
    default_detail = 'Validation error.'
    default_code = 'validation_error'


class NotFoundError(APIException):
    """Resource not found error."""
    status_code = 404
    default_detail = 'Resource not found.'
    default_code = 'not_found'


class UnauthorizedError(APIException):
    """Unauthorized access error."""
    status_code = 401
    default_detail = 'Authentication required.'
    default_code = 'unauthorized'


class ForbiddenError(APIException):
    """Forbidden access error."""
    status_code = 403
    default_detail = 'You do not have permission to perform this action.'
    default_code = 'forbidden'

