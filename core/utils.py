from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.db import IntegrityError
from django.core.exceptions import ValidationError as DjangoValidationError
import logging

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):

    response = exception_handler(exc, context)

    if response is None:
        if isinstance(exc, IntegrityError):
            logger.error(f"Database integrity error: {str(exc)}")

            return Response(
                {
                    "detail": "Database integrity error. This operation violates database constraints."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        elif isinstance(exc, DjangoValidationError):
            return Response(
                {"detail": exc.messages if hasattr(exc, "messages") else str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        elif isinstance(exc, Exception):

            logger.exception(f"Unexpected error: {str(exc)}")

            return Response(
                {"detail": "An unexpected error occurred."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    return response
