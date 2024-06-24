import uuid

from django.db import models
from django.core.validators import MinLengthValidator
from django.db.models import Q
from django.forms import model_to_dict


class User(models.Model):
    id = models.BigIntegerField(primary_key=True, unique=True)
    login = models.CharField(max_length=15, unique=True)
    displayName = models.CharField(
        max_length=25,
        validators=[MinLengthValidator(5, "Must contains at least 5 char")],
        null=True
    )

    @staticmethod
    def get_friends_ids(user_id) -> list | None:
        users = User.objects.filter(id=user_id)
        if not users.exists():
            return None
        current_user = users[0]
        q1 = Friendship.objects.filter(receiver=current_user, accepted=True)
        q2 = Friendship.objects.filter(sender=current_user, accepted=True)
        friends_ids = []
        for query in q1:
            friends_ids.append(query.sender)
        for query in q2:
            friends_ids.append(query.receiver)
        return friends_ids


class Friendship(models.Model):
    sender = models.ForeignKey(User, related_name='request_sender', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='request_receiver', on_delete=models.CASCADE)
    accepted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (['sender', 'receiver'], ['receiver', 'sender'])

    def to_dict(self):
        return {
            "Sender": model_to_dict(self.sender),
            "receiver": model_to_dict(self.receiver),
            "accepted": self.accepted
        }
