from django.http import response
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from user.models import User

import json


@csrf_exempt  # TODO: Not use in production
@require_POST
def create_user(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return response.HttpResponse(status=400, reason="Bad Json content: Decode Error")

    expected_keys = {"login", "display_name"}
    if set(data.keys()) != expected_keys:
        return response.HttpResponse(status=400, reason="Bad Json content: Bad Keys")

    login = data["login"]
    display_name = data["display_name"]

    if User.objects.filter(login=login).exists():
        return response.HttpResponse(status=401, reason="User with this login already exists")

    new_user = User(login=login, displayName=display_name)
    new_user.save()

    return response.HttpResponse(status=200)
