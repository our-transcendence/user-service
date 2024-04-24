import uuid

from django.db import models
from django.core.validators import MinLengthValidator


class User(models.Model):
    id = models.BigIntegerField(primary_key=True)
    login = models.CharField(max_length=15, unique=True)
    displayName = models.CharField(
        max_length=25,
        validators=[MinLengthValidator(5, "Must contains at least 5 char")],
        null=True
    )
