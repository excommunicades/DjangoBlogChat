import json
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin

class ErrorHandlingMiddleware(MiddlewareMixin):

    def process_exception(self, request, exception):

        error_code = getattr(exception, 'status_code', 500)

        error_mapping = {
            500: "HTTP_500_INTERNAL_SERVER_ERROR",
            501: "HTTP_501_NOT_IMPLEMENTED",
            502: "HTTP_502_BAD_GATEWAY",
            503: "HTTP_503_SERVICE_UNAVAILABLE",
            504: "HTTP_504_GATEWAY_TIMEOUT",
            505: "HTTP_505_HTTP_VERSION_NOT_SUPPORTED",
            506: "HTTP_506_VARIANT_ALSO_NEGOTIATES",
            507: "HTTP_507_INSUFFICIENT_STORAGE",
            508: "HTTP_508_LOOP_DETECTED",
            509: "HTTP_509_BANDWIDTH_LIMIT_EXCEEDED",
            510: "HTTP_510_NOT_EXTENDED",
            511: "HTTP_511_NETWORK_AUTHENTICATION_REQUIRED"
        }

        error_name = error_mapping.get(error_code, f"HTTP_{error_code}_UNKNOWN_ERROR")

        return JsonResponse(
            {
                "errors": {
                    "server": error_name,
                    "message": str(exception)
                },
                "status": f"{error_code}",
            },
            status=error_code
        )