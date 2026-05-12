from __future__ import annotations

import json

from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from apps.project.decorators import queryable
from apps.project.models import Project
from apps.project.repository import project as project_repo
from apps.project.serializers import serialize_project
from apps.users.decorators import require_auth


@require_http_methods(["GET"])
@require_auth
@queryable(
    serializer=serialize_project,
    filter_by_map={
        "name__icontains": "name",
        "description__icontains": "description",
        "date_start__gte": "date_start_after",
        "date_end__lte": "date_end_before",
        "technologies_used__contains": ("technology", lambda v: [v]),
    },
    order_by_map={
        "name": "order_by_name",
        "date_start": "order_by_date_start",
        "date_end": "order_by_date_end",
    },
    default_page_size=10,
)
def project_list(request: HttpRequest) -> QuerySet[Project]:
    return project_repo.get_all_for_user(request.user)


@csrf_exempt
@require_auth
@require_http_methods(["POST"])
def project_create(request: HttpRequest) -> HttpResponse:
    body = json.loads(request.body)
    project = project_repo.create(body, user=request.user)
    return JsonResponse(serialize_project(project), status=201)


@require_auth
@require_http_methods(["GET"])
def project_retrieve(request: HttpRequest, pk: int) -> HttpResponse:
    project = project_repo.get_by_id_for_user(pk, request.user)
    return JsonResponse(serialize_project(project))


@csrf_exempt
@require_auth
@require_http_methods(["PUT", "PATCH"])
def project_update(request: HttpRequest, pk: int) -> HttpResponse:
    project = project_repo.get_by_id_for_user(pk, request.user)
    body = json.loads(request.body)
    project = project_repo.update(project, body, partial=request.method == "PATCH")
    return JsonResponse(serialize_project(project))


@csrf_exempt
@require_auth
@require_http_methods(["DELETE"])
def project_delete(request: HttpRequest, pk: int) -> HttpResponse:
    project_repo.delete(project_repo.get_by_id_for_user(pk, request.user))
    return HttpResponse(status=204)
