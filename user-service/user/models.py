import uuid

from django.db import models



class User(models.Model):
    id = models.BigIntegerField(primary_key=True, unique=True)
    login = models.CharField(max_length=15, unique=True)
    displayName = models.CharField(
        max_length=25,
        validators=[MinLengthValidator(5, "Must contains at least 5 char")],
        null=True
    )



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
