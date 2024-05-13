from django.db.models import Q
from django.http import response, HttpRequest, HttpResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_http_methods
from user.models import User, Friend

import json
import requests

import ourJWT.OUR_exception

from userService import settings
from ..utils import get_user_from_jwt

from django.db.models import Q
from django.db.models import F

NO_USER = 404, "No user found with given ID"
JSON_DECODE_ERROR = 400, "JSON Decode Error"
JSON_BAD_KEYS = 400, "JSON Bad Keys"
USER_EXISTS = 401, "User with this login already exists"
BAD_IDS = 400, "User id is not equal with connected user id"
CANT_CONNECT_AUTH = 408, "Cant connect to auth-service"
ONLY_PNG = 400, "Only png images are allowed"

@csrf_exempt  # TODO: Not use in production
@require_POST
def create_user(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError as e:
        return response.HttpResponse(*JSON_DECODE_ERROR)

    expected_keys = {"id", "login"}
    if set(data.keys()) != expected_keys:
        return response.HttpResponse(*JSON_DECODE_ERROR)

    user_id = data["id"]
    login = data["login"]

    if User.objects.filter(Q(login=login) | Q(id=user_id)).exists():
        return response.HttpResponse(*USER_EXISTS)

    new_user = User(id=user_id, login=login, displayName=login)
    new_user.save()

    return response.HttpResponse()


@require_http_methods(["GET"])
def get_user(request, user_id):
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return response.HttpResponse(*NO_USER)
    return response.JsonResponse({"id": user.id, "login": user.login, "displayName": user.displayName})


@csrf_exempt
@ourJWT.Decoder.check_auth()
@require_http_methods(["POST"])
def update_user(request: HttpRequest, user_id, **kwargs):
    try:
        user = get_user_from_jwt(kwargs)
    except Http404:
        return response.HttpResponse(*NO_USER)
    if user.id != user_id:
        return response.HttpResponse(*BAD_IDS)
    if 'picture' in request.FILES.keys():
        if request.FILES['picture'].content_type != 'image/png':
            return HttpResponse(*ONLY_PNG)
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
@ourJWT.Decoder.check_auth()
@require_http_methods(["DELETE"])
def delete_user(request, user_id, **kwargs):
    try:
        user = get_user_from_jwt(kwargs)
    except Http404:
        return response.HttpResponse(*NO_USER)
    if user.id != user_id:
        return response.HttpResponse(*BAD_IDS)
    try:
        delete_response = requests.delete(f"{settings.AUTH_SERVICE_URL}/{user_id}/delete", verify=False)
    except requests.exceptions.ConnectionError as e:
        return response.HttpResponse(*CANT_CONNECT_AUTH)
    if delete_response.status_code != 200:
        return response.HttpResponse(status=delete_response.status_code, reason=delete_response.text)
    user.delete()
    return response.HttpResponse()

@csrf_exempt
@ourJWT.Decoder.check_auth()
@require_http_methods(["GET"])
def get_friends(request, **kwargs):
    try:
        user = get_user_from_jwt(kwargs)
    except Http404:
        return response.HttpResponse(*NO_USER)
    # get all the friends and return them

    Friend.objects.filter(
        Q(user__friend__user=F('friend')) &
        Q(friend__user__friend=F('user')) &
        Q(user=user.id)
    )
    return response.HttpResponse()

@csrf_exempt
@ourJWT.Decoder.check_auth()
@require_http_methods(["GET"])
def get_friend_rec(request, user_id, **kwargs):
    try:
        user = get_user_from_jwt(kwargs)
    except Http404:
        return response.HttpResponse(*NO_USER)
    if user.id != user_id:
        return response.HttpResponse(*BAD_IDS)
    # get all the friends requests you received
    return response.HttpResponse()

@csrf_exempt
@ourJWT.Decoder.check_auth()
@require_http_methods(["GET"])
def get_friend_send(request, user_id, **kwargs):
    try:
        user = get_user_from_jwt(kwargs)
    except Http404:
        return response.HttpResponse(*NO_USER)
    if user.id != user_id:
        return response.HttpResponse(*BAD_IDS)
    # get all the friends requests you sent
    return response.HttpResponse()

@csrf_exempt
@ourJWT.Decoder.check_auth()
@require_http_methods(["GET"])
def add_friend(request, user_id, friend_id, **kwargs):
    try:
        user = get_user_from_jwt(kwargs)
    except Http404:
        return response.HttpResponse(*NO_USER)
    if user.id != user_id:
        return response.HttpResponse(*BAD_IDS)
    # add the relation user_id to friend_id
    return response.HttpResponse()