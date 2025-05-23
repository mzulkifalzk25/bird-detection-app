from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import ValidationError
from django.db import IntegrityError
from rest_framework.permissions import IsAuthenticated

class BaseAPIView(APIView):
    """
    Base view class that provides common error handling and functionality
    """
    permission_classes = [IsAuthenticated]

    def handle_exception(self, exc):
        """
        Handle common exceptions
        """
        if isinstance(exc, ObjectDoesNotExist):
            return Response({
                'error': 'Not Found',
                'detail': str(exc),
                'status_code': status.HTTP_404_NOT_FOUND
            }, status=status.HTTP_404_NOT_FOUND)

        if isinstance(exc, ValidationError):
            return Response({
                'error': 'Validation Error',
                'detail': str(exc),
                'status_code': status.HTTP_400_BAD_REQUEST
            }, status=status.HTTP_400_BAD_REQUEST)

        if isinstance(exc, IntegrityError):
            return Response({
                'error': 'Database Error',
                'detail': 'A database error occurred',
                'status_code': status.HTTP_400_BAD_REQUEST
            }, status=status.HTTP_400_BAD_REQUEST)

        return super().handle_exception(exc)

    def get_object_or_404(self, queryset, **kwargs):
        """
        Get object or return 404
        """
        try:
            return queryset.get(**kwargs)
        except ObjectDoesNotExist:
            raise Http404("Object not found")

    def validate_required_fields(self, data, required_fields):
        """
        Validate required fields in request data
        """
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            raise ValidationError(f"Missing required fields: {', '.join(missing_fields)}")