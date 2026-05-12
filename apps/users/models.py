from __future__ import annotations

import secrets

from django.contrib.auth.models import User
from django.db import models


class AuthToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="auth_tokens")
    token = models.CharField(max_length=64, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    @classmethod
    def generate_token(cls) -> str:
        return secrets.token_hex(32)
