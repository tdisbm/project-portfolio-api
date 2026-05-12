from django.urls import path

from apps.project import views

app_name = "project"

urlpatterns = [
    path("", views.project_list, name="project-list"),
    path("create/", views.project_create, name="project-create"),
    path("<int:pk>/", views.project_retrieve, name="project-retrieve"),
    path("<int:pk>/update/", views.project_update, name="project-update"),
    path("delete/<int:pk>/", views.project_delete, name="project-delete"),
]
