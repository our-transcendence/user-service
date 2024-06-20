from django.shortcuts import get_object_or_404
from user.models import User, Friendship

def get_user_from_jwt(kwargs):
    auth = kwargs["token"]
    key = auth["id"]
    user = get_object_or_404(User, pk=key)
    return user

def validate_friendship(friendship):
    friendship.accepted = True
    friendship.save()

def update_DN_in_service(new_DN: str):
    # update in auth

    # update in stats

    # update in history
    pass
