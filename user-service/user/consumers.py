import json
from http.cookies import SimpleCookie
from userService import settings
import jwt
from channels.generic.websocket import AsyncWebsocketConsumer
from django.core.cache import cache


class StatusConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.id = None
        # self.display_name = None
        self.username = None

    async def connect(self):
        print("WS CONNNECT", flush=True)
        i = 0
        while i < len(self.scope['headers']) and self.scope['headers'][i][0].decode() != "cookie":
            i += 1
        if i >= len(self.scope['headers']):
            await self.close(reason="no cookies")
            print("closed no cookies", flush=True)
            return
        cookies = SimpleCookie()
        cookies.load(self.scope['headers'][i][1].decode())
        for name, content in cookies.items():
            print(f"{name}: {content.value}", flush=True)
            if name == "auth_token":
                token = jwt.decode(content.value, settings.PUB_KEY, algorithms=["RS256"], issuer="OUR_Transcendence")
                self.username = token['login']
                # self.display_name = token['displayName']
                self.id = token['id']
        await self.accept()
        print("accepted", flush=True)
        cache.set(self.id, "connected")
        # SEND status de tous les amis de id
        # send to tous les amis de id "id just connected"

    async def disconnect(self, code):

        cache.set(self.id, "disconnected")
        # send message to all ami de id "id just disconnected"
