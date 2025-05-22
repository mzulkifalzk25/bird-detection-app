from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from rest_framework.exceptions import APIException
from django.http import Http404
from rest_framework.exceptions import PermissionDenied
from rest_framework.exceptions import NotAuthenticated
from rest_framework.exceptions import NotFound
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.exceptions import ParseError
from rest_framework.exceptions import Throttled
from rest_framework.exceptions import ValidationError as DRFValidationError

def custom_exception_handler(exc, context):
    """
    Custom exception handler for consistent error responses
    """
    if isinstance(exc, Http404):
        exc = NotFound()
    elif isinstance(exc, PermissionDenied):
        exc = PermissionDenied()
    elif isinstance(exc, NotAuthenticated):
        exc = NotAuthenticated()
    elif isinstance(exc, MethodNotAllowed):
        exc = MethodNotAllowed(method=exc.method)
    elif isinstance(exc, ParseError):
        exc = ParseError()
    elif isinstance(exc, Throttled):
        exc = Throttled()
    elif isinstance(exc, ValidationError):
        exc = DRFValidationError(detail=exc.message_dict)
    elif isinstance(exc, IntegrityError):
        exc = DRFValidationError(detail="Database integrity error occurred")
    elif isinstance(exc, APIException):
        pass
    else:
        exc = APIException(detail=str(exc))

    # Get the standard error response
    response = exception_handler(exc, context)

    if response is None:
        return Response({
            'error': 'Internal Server Error',
            'detail': str(exc),
            'status_code': status.HTTP_500_INTERNAL_SERVER_ERROR
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Add error code to response
    if not isinstance(response.data, dict):
        response.data = {'detail': response.data}

    response.data['error'] = exc.__class__.__name__
    response.data['status_code'] = response.status_code

    return response