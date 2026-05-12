from django.http import HttpRequest, JsonResponse


def index(request: HttpRequest) -> JsonResponse:
    return JsonResponse({"service": "project-portfolio-api", "status": "ok"})


def health(request: HttpRequest) -> JsonResponse:
    return JsonResponse({"status": "ok"})
