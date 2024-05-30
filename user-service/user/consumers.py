import json
from http.cookies import SimpleCookie
from user.models import User
from userService import settings
import jwt
import channels.generic.websocket import WebsocketConsumer

class ChatConsumer(WebsocketConsumer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.id = None
        self.display_name = None
        self.username = None
    async def connect(self):
        i = 0
        while i < len(self.scope['headers']) and self.scope['headers'][i][0].decode() != "cookie":
            i += 1
        print(self.scope['headers'], flush=True)
        if i >= len(self.scope['headers']):
            await self.close(reason="no cookies")
            return
        print(f"{self.scope['headers'][i][0].decode()}: {self.scope['headers'][i][1].decode()}", flush=True)
        cookies = SimpleCookie()
        cookies.load(self.scope['headers'][i][1].decode())
        for name, content in cookies.items():
            print(f"{name}: {content.value}", flush=True)
            if name == "auth_token":
                token = jwt.decode(content.value, settings.PUB_KEY, algorithms=["RS256"], issuer="OUR_Transcendence")
                print(token, flush=True)
                self.username = token['login']
                self.display_name = token['displayName']
                self.id = token['id']
        await self.channel_layer.group_add(self.username, self.channel_name)
        await self.accept()
        self.accept()

        self.send(text_data=json.dumps({
            'type':'connection_established',
            'message':'you are now connected'
        }))
        my_user = User.objets.get(self.id)
        my_user.connected = True
        my_user.save()

    async def disconnect(self, code):
        my_user = User.objets.get(self.id)
        my_user.connected = False
        my_user.save()