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

class Friend(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='friends')
    friend = models.ForeignKey(User, on_delete=models.CASCADE, related_name='friends_with')
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ('user', 'friend')
    def __str__(self):
        return f"{self.user.login} is friends with {self.friend.login}"
