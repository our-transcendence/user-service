import os

from django.db import OperationalError
from django.db.models import Q
from django.core import serializers
from django.shortcuts import get_object_or_404
from django.http import response, HttpRequest, Http404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_http_methods
from user.models import User, Friendship

import json
import requests

import ourJWT.OUR_exception

from userService import settings
from user.utils import get_user_from_jwt, validate_friendship

from django.db.models import Q
from django.db.models import F

NO_USER = 404, "No user found with given ID"
JSON_DECODE_ERROR = 400, "JSON Decode Error"
JSON_BAD_KEYS = 400, "JSON Bad Keys"
USER_EXISTS = 401, "User with this login already exists"
BAD_IDS = 400, "User id is not equal with connected user id"
CANT_CONNECT_AUTH = 408, "Cant connect to auth-service"
ONLY_PNG = 400, "Only png images are allowed"
ALREADY_FRIEND = 400, "Both user are already friend"
NOT_FRIEND = 400, "No friendship beetwen both id"
SAME_USER = 403, "Friend and user are the same"
DB_FAILURE =  503, "Database Failure"
ALREADY_ASKED = 409, "Friendship already asked"

@csrf_exempt
@ourJWT.Decoder.check_auth()
@require_http_methods(["POST"])
def add_friend(request, friend_id, **kwargs):
    try:
        user = get_user_from_jwt(kwargs)
        friend = get_object_or_404(User, pk=friend_id)
    except Http404:
        return response.HttpResponse(*NO_USER)

    if user.id == friend.id:
        return response.HttpResponse(*SAME_USER)

    #regarder si user et friend sont deja amis
    if Friendship.objects.filter(
        Q(sender=user, receiver=friend, accepted=True) |
        Q(sender=friend, receiver=user, accepted=True)
    ).exists():
        return response.HttpResponse(*ALREADY_FRIEND)

    #regarder si friend a deja demande user en ami
    asked = Friendship.objects.filter(
        Q(sender=friend, receiver=user, accepted=False)
    ).count()

    if asked == 1:
        try:
            validate_friendship()
        except OperationalError as e:
            print(f"DATABASE FAILURE {e}", flush=True)
            return response.HttpResponse(*DB_FAILURE)
        return response.HttpResponse()

    #regarder si user a deja demande friend en ami
    if Friendship.objects.filter(
        Q(sender=user, receiver=friend, accepted=False)
    ).exists():
        return response.HttpResponse(*ALREADY_ASKED)

    new_request = Friendship(sender=user, receiver=friend)
    try:
        new_request.save()
    except OperationalError as e:
        print(f"DATABASE FAILURE {e}", flush=True)
        return response.HttpResponse(*DB_FAILURE)
    return response.HttpResponse()

@csrf_exempt
@ourJWT.Decoder.check_auth()
@require_http_methods(["POST"])
def accept_friend(request, friend_id, **kwargs):
    try:
        user = get_user_from_jwt(kwargs)
        friend = get_object_or_404(User, pk=friend_id)
        friend_request = get_object_or_404(Friendship, sender=friend, receiver=user, accepted=False)
    except Http404:
        return response.HttpResponse(*NO_USER)

    try:
        validate_friendship(friend_request)
    except OperationalError:
        return response.HttpResponse(status=503, reason="Can't connect to Database")

    return response.HttpResponse()

@csrf_exempt
@ourJWT.Decoder.check_auth()
@require_http_methods(["POST"])
def refuse_friend(request, friend_id, **kwargs):
    try:
        user = get_user_from_jwt(kwargs)
        friend = get_object_or_404(User, pk=friend_id)
        friend_request = get_object_or_404(Friendship, sender=friend, receiver=user, accepted=False)
    except Http404:
        return response.HttpResponse(*NO_USER)

    try:
        friend_request.delete()
    except OperationalError:
        return response.HttpResponse(status=503, reason="Can't connect to Database")

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

    q1 = Friendship.objects.filter(
        Q(sender=user) | Q(receiver=user, accepted=True)
    )

    if not q1.exists():
        return response.HttpResponse(200, "User has no friend, that's sad")
    data = {friend.pk : friend.to_dict() for friend in q1}

    return response.JsonResponse(data=data)


@csrf_exempt
@ourJWT.Decoder.check_auth()
@require_http_methods(["POST"])
def delete_friend(request, friend_id, **kwargs):
    try:
        user = get_user_from_jwt(kwargs)
        friend = get_object_or_404(User, pk=friend_id)
    except Http404:
        return response.HttpResponse(*NO_USER)

    query= Friendship.objects.filter(
        Q(sender=user, receiver=friend)|Q(sender=friend, receiver=user)
    )

    if not query.exists():
        return response.HttpResponse(*NOT_FRIEND)
    try:
        query.delete()
    except OperationalError as e:
        print(f"DATABASE FAILURE {e}", flush=True)
        return response.HttpResponse(*DB_FAILURE)
    return response.HttpResponse()
