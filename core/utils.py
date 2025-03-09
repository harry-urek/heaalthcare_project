from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.db import IntegrityError
from django.core.exceptions import ValidationError as DjangoValidationError
import logging

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    The `custom_exception_handler` function handles different types of exceptions and returns
    appropriate responses based on the exception type.

    :param exc: The `exc` parameter in the `custom_exception_handler` function represents the exception
    that was raised during the execution of the code. It could be any type of exception such as
    `IntegrityError`, `DjangoValidationError`, or a generic `Exception`. The function handles different
    types of exceptions and generates
    :param context: The `context` parameter in the `custom_exception_handler` function typically refers
    to the request context or the context in which the exception occurred. It contains information about
    the request, such as the request data, user information, and other relevant details that can help in
    handling the exception appropriately. This context is
    :return: The custom_exception_handler function returns a Response object based on the type of
    exception that occurred. If the exception is an IntegrityError, it returns a response indicating a
    database integrity error. If the exception is a DjangoValidationError, it returns a response with
    the error messages. If the exception is of type Exception, it returns a response indicating an
    unexpected error. If none of these conditions are met, it returns
    """

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
