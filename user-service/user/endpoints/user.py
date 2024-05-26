import os
import shutil
import json
import requests

from django.db.models import Q
from django.db import OperationalError
from django.core import serializers
from django.http import response, HttpRequest, HttpResponse, Http404
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_http_methods
from user.models import User


import ourJWT.OUR_exception

from userService import settings
from user.utils import get_user_from_jwt


NO_USER = 404, "No user found with given ID"
JSON_DECODE_ERROR = 400, "JSON Decode Error"
JSON_BAD_KEYS = 400, "JSON Bad Keys"
USER_EXISTS = 406, "User with this login already exists"
BAD_IDS = 400, "User id is not equal with connected user id"
CANT_CONNECT_AUTH = 408, "Cant connect to auth-service"
CANT_CONNECT_STATS = 408, "Cant connect to stats-service"
ONLY_PNG = 400, "Only png images are allowed"
DB_FAILURE =  503, "Database Failure"

SERVICE_KEY = os.getenv("INTER_SERVICE_KEY")

@csrf_exempt  # TODO: Not use in production
@require_POST
def create_user(request):
    authorisation = request.headers.get("Authorization")
    if authorisation is None or authorisation != SERVICE_KEY:
        return response.HttpResponseForbidden()

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError as e:
        return response.HttpResponse(*JSON_DECODE_ERROR)

    expected_keys = {"id", "login", "display_name"}
    if set(data.keys()) != expected_keys:
        return response.HttpResponse(*JSON_DECODE_ERROR)

    user_id = data["id"]
    login = data["login"]
    display_name = data["display_name"]

    if User.objects.filter(Q(login=login) | Q(id=user_id)).exists():
        return response.HttpResponse(*USER_EXISTS)

    new_user = User(id=user_id, login=login, displayName=display_name)
    try:
        new_user.save()
    except OperationalError as e:
        print(f"DATABASE FAILURE {e}", flush=True)
        return response.HttpResponse(*DB_FAILURE)

    # add default picture
    try:
        cat_request = requests.get("https://cataas.com/cat?type=square&position=center", timeout=5)
        if (cat_request.status_code / 100) % 10 != 2:
            raise Exception("Cataas request failed")
        with open(f"{settings.PICTURES_DST}/{new_user.id}.png", "wb+") as f:
            f.write(cat_request.content)
    except Exception as e:
        print(f"CAT FAILURE {e}", flush=True)
        shutil.copyfile("/data/default.png", f"{settings.PICTURES_DST}/{new_user.id}.png")
    return response.HttpResponse()


@require_http_methods(["GET"])
def get_user(request, user_id):
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return response.HttpResponse(*NO_USER)
    return response.JsonResponse({"id": user.id, "login": user.login, "displayName": user.displayName, "connected": user.connected})


@csrf_exempt
@ourJWT.Decoder.check_auth()
@require_http_methods(["POST"])
def update_user(request: HttpRequest, **kwargs):
    try:
        user = get_user_from_jwt(kwargs)
    except Http404:
        return response.HttpResponse(*NO_USER)

    if 'picture' in request.FILES.keys():
        if request.FILES['picture'].content_type != 'image/png':
            return HttpResponse(*ONLY_PNG)
        with open(f"{settings.PICTURES_DST}/{user.id}.png", "wb+") as f:
            for chunk in request.FILES["picture"]:
                f.write(chunk)
    if 'display_name' in request.POST.keys():
        user.displayName = request.POST['display_name']
    try:
        user.save()
    except OperationalError as e:
        print(f"DATABASE FAILURE {e}", flush=True)
        return response.HttpResponse(*DB_FAILURE)

    return response.HttpResponse()


@csrf_exempt
@require_http_methods(["GET"])
def get_picture(request, user_id):
    try:
        user = get_object_or_404(User, pk=user_id)
    except Http404:
        return response.HttpResponse(*NO_USER)
    try:
        with open(f"{settings.PICTURES_DST}/{user.id}.png", "rb") as f:
            return HttpResponse(f.read(), content_type="image/png")
    except FileNotFoundError:
        return response.HttpResponse(status=404, reason="No picture found")

@csrf_exempt
@ourJWT.Decoder.check_auth()
@require_http_methods(["DELETE"])
def delete_user(request, **kwargs):
    print(request.method, flush=True)
    try:
        user:User = get_user_from_jwt(kwargs)
    except Http404:
        return response.HttpResponse(*NO_USER)

    #delete user from auth-service
    try:
        delete_header = {"Authorization": SERVICE_KEY}
        auth_response = requests.delete(f"{settings.AUTH_SERVICE_URL}/delete/{user.id}",
                                          headers=delete_header,
                                          verify=False)
    except requests.exceptions.ConnectionError as e:
        return response.HttpResponse(*CANT_CONNECT_AUTH)
    if auth_response.status_code != 200:
        return response.HttpResponse(status=auth_response.status_code, reason=auth_response.text)

    #delete user from stats service
    try:
        stats_response = requests.delete(f"{settings.STATS_SERVICE_URL}/stats/{user.id}/delete",
                                          headers=delete_header,
                                          verify=False)
    except requests.exceptions.ConnectionError as e:
        return response.HttpResponse(*CANT_CONNECT_STATS)
    if stats_response.status_code != 200:
        return response.HttpResponse(status=stats_response.status_code, reason=stats_response.text)

    #delete user from history service
    try:
        delete_data = {"player_id": user.id}
        history_response: requests.Response = requests.delete(f"{settings.HISTORY_SERVICE_URL}/playerdelete",
                                          headers=delete_header,
                                          data=json.dumps(delete_data),
                                          verify=False)
    except requests.exceptions.ConnectionError as e:
        return response.HttpResponse(*CANT_CONNECT_STATS)
    if history_response.status_code != 200:
        return response.HttpResponse(status=history_response.status_code, reason=history_response.reason)

    try:
        user.delete()
    except OperationalError as e:
        print(f"DATABASE FAILURE {e}", flush=True)
        return response.HttpResponse(*DB_FAILURE)
    if os.path.exists(f"{settings.PICTURES_DST}/{user.id}.png"):
        os.remove(f"{settings.PICTURES_DST}/{user.id}.png")
    return response.HttpResponse()
