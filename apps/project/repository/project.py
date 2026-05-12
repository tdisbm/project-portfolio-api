from __future__ import annotations

from typing import Any

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db.models import QuerySet

from apps.project.models import Project
from apps.project.serializers import validate_project_data


def get_all_for_user(user: User) -> QuerySet[Project]:
    return Project.objects.filter(user=user)


def get_by_id_for_user(pk: int, user: User) -> Project:
    return Project.objects.get(pk=pk, user=user)


def create(data: dict[str, Any], user: User) -> Project:
    cleaned, errors = validate_project_data(data)
    if errors:
        raise ValidationError(errors)
    return Project.objects.create(user=user, **cleaned)


def update(project: Project, data: dict[str, Any], *, partial: bool = False) -> Project:
    cleaned, errors = validate_project_data(data, partial=partial)
    if errors:
        raise ValidationError(errors)
    for field, value in cleaned.items():
        setattr(project, field, value)
    project.save()
    return project


def delete(project: Project) -> None:
    project.delete()
