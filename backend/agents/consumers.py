# agents/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer

class CallStatusConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"] # user object from Django's ASGI middleware

        if not self.user.is_authenticated:
            await self.close() # close connection if user is not authenticated
            return

        self.group_name = f"user_{self.user.id}" # Group name unique to this user

        # Join user group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()
        print(f"WebSocket connected for user: {self.user.username}, group: {self.group_name}")


    async def disconnect(self, close_code):
        # Leave user group
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )
        print(f"WebSocket disconnected for user: {self.user.username}, group: {self.group_name}")

    # Receive message from WebSocket
    async def receive(self, text_data):
        # for this project, the client doesn't send messages *to* the backend via WebSocket.
        # it only receives updates.
        pass

    # Receive message from channel layer group
    async def send_message(self, event):
        message = event['message']
        # Send message to WebSocket
        await self.send(text_data=json.dumps(message))