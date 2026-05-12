from django.conf import settings
from django.db import models

from apps.core.models import TimeStampedModel


class Project(TimeStampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="projects",
        null=True,
    )
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    technologies_used = models.JSONField(default=list)
    date_start = models.DateField()
    date_end = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ["-date_start"]

    def __str__(self) -> str:
        return self.name
