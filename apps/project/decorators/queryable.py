from __future__ import annotations

import inspect
from collections.abc import Callable
from functools import wraps
from typing import Any, TypeVar

from django.core.paginator import Page, Paginator
from django.db.models import Q, QuerySet
from django.http import HttpRequest, JsonResponse, QueryDict

T = TypeVar("T")

# A filter spec is either:
#   - a plain param name (str): value passed as-is to the ORM lookup
#   - a (param_name, transform) tuple: each value from getlist is passed through
#     transform before being used in the ORM lookup
FilterSpec = str | tuple[str, Callable[[str], Any]]


def _apply_filters(
    qs: QuerySet[T],
    filters: dict[str, FilterSpec],
    request_params: QueryDict,
) -> QuerySet[T]:
    for lookup, spec in filters.items():
        if isinstance(spec, tuple):
            param_name, transform = spec
        else:
            param_name, transform = spec, lambda v: v

        values = request_params.getlist(param_name)
        if not values:
            continue

        q = Q()
        for value in values:
            q |= Q(**{lookup: transform(value)})
        qs = qs.filter(q)

    return qs


def _apply_ordering(
    qs: QuerySet[T],
    orderings: dict[str, str],
    request_params: QueryDict,
) -> QuerySet[T]:
    order_fields: list[str] = []
    for field, param_name in orderings.items():
        direction = request_params.get(param_name)
        if direction is not None:
            order_fields.append(f"-{field}" if direction == "desc" else field)
    return qs.order_by(*order_fields) if order_fields else qs


def _apply_pagination(
    qs: QuerySet[T],
    default_page_size: int,
    request_params: QueryDict,
) -> tuple[Page[T], Paginator[T]]:
    page_size = int(request_params.get("page_size", default_page_size))
    page_number = int(request_params.get("page", 1))

    if page_size < 1:
        page_size = default_page_size
    if page_number < 1:
        page_number = 1

    paginator: Paginator[T] = Paginator(qs, page_size)
    return paginator.get_page(page_number), paginator


def queryable(
    serializer: Callable[[Any], Any],
    filter_by_map: dict[str, FilterSpec] | None = None,
    order_by_map: dict[str, str] | None = None,
    default_page_size: int = 10,
) -> Callable[[Callable[..., Any]], Callable[..., JsonResponse]]:
    """
    Decorator for list views. The wrapped view must return a QuerySet.

    Applies ORM filters and ordering driven by query parameters, then paginates
    the result and returns a JsonResponse.

    ``filter_by_map`` maps a Django ORM lookup expression to either a param name
    or a ``(param_name, transform)`` tuple.  When a tuple is used, every value
    returned by ``getlist(param_name)`` is passed through ``transform`` before
    being applied to the lookup, and each value produces its own OR clause::

        @queryable(
            serializer=serialize_project,
            filter_by_map={
                "name__icontains": "name",
                "date_start__gte": "date_start_after",
                "technologies_used__contains": ("technology", lambda v: [v]),
            },
            order_by_map={
                "date_start": "order_by_date_start",
            },
            default_page_size=20,
        )

    ``order_by_map`` maps an ORM field expression to a query parameter name.
    When the parameter is present its value is used as the sort direction:
    ``"asc"`` (or absent direction) applies ascending order; ``"desc"`` applies
    descending order.

    A filter or ordering is skipped when the corresponding query parameter is absent.
    """
    _filters = filter_by_map or {}
    _orderings = order_by_map or {}

    def decorator(view_func: Callable[..., Any]) -> Callable[..., JsonResponse]:
        _accepts_request = "request" in inspect.signature(view_func).parameters

        @wraps(view_func)
        def wrapper(request: HttpRequest, *args: Any, **kwargs: Any) -> JsonResponse:
            qs: QuerySet[Any] = (
                view_func(request, *args, **kwargs)
                if _accepts_request
                else view_func(*args, **kwargs)
            )

            qs = _apply_filters(qs, _filters, request.GET)
            qs = _apply_ordering(qs, _orderings, request.GET)

            page, paginator = _apply_pagination(qs, default_page_size, request.GET)

            return JsonResponse(
                {
                    "count": paginator.count,
                    "total_pages": paginator.num_pages,
                    "page": page.number,
                    "page_size": paginator.per_page,
                    "results": [serializer(p) for p in page.object_list],
                }
            )

        return wrapper

    return decorator
