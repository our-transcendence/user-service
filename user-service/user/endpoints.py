from django.db.models import Q
from django.http import response, HttpRequest, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_http_methods
from user.models import User

import json
import requests

from userService import settings


@csrf_exempt  # TODO: Not use in production
@require_POST
def create_user(request):
    print(request.body, flush=True)
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError as e:
        print (e, flush=True)
        return response.HttpResponse(status=400, reason="Bad Json content: Decode Error")

    expected_keys = {"id", "login"}
    if set(data.keys()) != expected_keys:
        return response.HttpResponse(status=400, reason="Bad Json content: Bad Keys")

    user_id = data["id"]
    login = data["login"]

    if User.objects.filter(Q(login=login) | Q(id=user_id)).exists():
        return response.HttpResponse(status=401, reason="User with this login already exists")

    new_user = User(id=user_id, login=login, displayName=login)
    new_user.save()

    return response.HttpResponse(status=200)


@require_http_methods(["GET"])
def get_user(request, user_id):
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return response.HttpResponse(status=404)
    return response.JsonResponse({"id": user.id, "login": user.login, "displayName": user.displayName})


@csrf_exempt
@require_http_methods(["POST"])
def update_user(request: HttpRequest, user_id):
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return response.HttpResponse(status=404)
    if 'picture' in request.FILES.keys():
        if request.FILES['picture'].content_type != 'image/png':
            return HttpResponse(status=400, reason="Only png images are allowed")
        with open(f"{settings.PICTURES_DST}/{user_id}.png", "wb+") as f:
            for chunk in request.FILES["picture"]:
                f.write(chunk)
    if 'display_name' in request.POST.keys():
        user.displayName = request.POST['display_name']
    user.save()
    return response.HttpResponse()


@csrf_exempt
@require_http_methods(["GET"])
def get_picture(request, user_id):
    with open(f"{settings.PICTURES_DST}/{user_id}.png", "rb") as f:
        return HttpResponse(f.read(), content_type="image/png")

@csrf_exempt
@require_http_methods(["DELETE"])
def delete_user(request, user_id):
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return response.HttpResponse(status=404)
    # TODO si on est pas authentifie, 401, unauthorized
    try:
        delete_response = requests.delete(f"{settings.AUTH_SERVICE_URL}/{user_id}/delete", verify=False)
    except requests.exceptions.ConnectionError as e:
        print(e)
        return response.HttpResponse(status=400, reason="Cant connect to auth-service")
    if delete_response.status_code != 200:
        return response.HttpResponse(status=delete_response.status_code, reason=delete_response.text)
    user.delete()
    return response.HttpResponse()
