from __future__ import annotations

import json
import traceback

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.http import HttpRequest, JsonResponse


class JsonExceptionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest):
        return self.get_response(request)

    def process_exception(self, request: HttpRequest, exception: Exception) -> JsonResponse | None:
        if isinstance(exception, ObjectDoesNotExist):
            return JsonResponse({"detail": "Not found."}, status=404)
        if isinstance(exception, ValidationError):
            return JsonResponse({"errors": exception.messages}, status=422)
        if isinstance(exception, (json.JSONDecodeError, UnicodeDecodeError)):
            return JsonResponse({"detail": "Invalid JSON body."}, status=400)

        if settings.DEBUG:
            return JsonResponse(
                status=500,
                data={
                    "detail": str(exception),
                    "exception": type(exception).__name__,
                    "traceback": traceback.format_exc(),
                },
            )

        return JsonResponse({"detail": "Internal server error."}, status=500)
