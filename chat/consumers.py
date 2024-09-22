# chat/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from . import models


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Get the url parameters
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        # Generate group name
        self.room_group_name = f'chat_{self.room_name}'
        # Create a new group model instance if it not exsit.
        await self.create_group_if_not_exists(self.room_group_name)
        
        # Join the room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave the room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        try:
            # Access current user using "self.scope['user']"
            self.user = self.scope['user']
            
            # Authenticated the user.
            if self.user.is_authenticated:
                # Try to parse JSON from the WebSocket message
                text_data_json = json.loads(text_data)
                message = text_data_json.get('message')
                
                # Find group name and creating new chat instance
                # We need to use database_sync_to_async() for any type of DB query
                group = await database_sync_to_async(models.Group.objects.get)(name=self.room_group_name)
                # Create new chat instance
                await database_sync_to_async(models.Chat.objects.create)(content=message, group=group)
                if message:
                    # Broadcast the message to the group
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            'type': 'chat_message',
                            'message': message
                        }
                    )
            else:
                # Send an error message if the user is not authenticated
                await self.send(text_data=json.dumps({
                    'message': 'Authentication is required!'
                }))
        except json.JSONDecodeError:
            # Handle JSON decoding error (bad format, empty body)
            await self.send(text_data=json.dumps({
                'error': 'Invalid JSON format or empty message.'
            }))

    # Send message from room group
    async def chat_message(self, event):
        message = event['message']
        print('chat message...')
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'user':self.user.username
        }))

    @database_sync_to_async
    def create_group_if_not_exists(self, group_name):
        if not models.Group.objects.filter(name=group_name).exists():
            group = models.Group(name=group_name)
            group.save()