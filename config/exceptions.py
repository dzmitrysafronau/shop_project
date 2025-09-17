from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    """Кастомный обработчик ошибок DRF с единым JSON-ответом."""
    drf_response = exception_handler(exc, context)

    if drf_response is not None:
        if isinstance(exc, ValidationError):
            drf_response.status_code = status.HTTP_422_UNPROCESSABLE_ENTITY

        detail_payload = drf_response.data

        final = Response(
            {
                "error": {
                    "type": exc.__class__.__name__,
                    "status": drf_response.status_code,
                    "detail": detail_payload,
                    "method": getattr(context.get("request"), "method", None),
                    "path": getattr(context.get("request"), "path", None),
                }
            },
            status=drf_response.status_code,
            content_type="application/json",
        )
        for k, v in drf_response.items():
            final[k] = v
        return final

    return Response(
        {
            "error": {
                "type": exc.__class__.__name__,
                "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "detail": "Internal Server Error",
                "method": getattr(context.get("request"), "method", None),
                "path": getattr(context.get("request"), "path", None),
            }
        },
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content_type="application/json",
    )
