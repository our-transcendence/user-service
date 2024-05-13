from django.shortcuts import get_object_or_404
from user.models import User
def get_user_from_jwt(kwargs):
    auth = kwargs["token"]
    key = auth["id"]
    user = get_object_or_404(User, pk=key)
    return user
