import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myekiva.settings')  # Replace 'myekiva' with your project name
django.setup()
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from django.contrib.auth import get_user_model
from .models import ChatMessage  # Make sure you created this model


User = get_user_model()

@sync_to_async
def get_user(user_id):
    return User.objects.get(id=user_id)

@sync_to_async
def save_message(sender, receiver_id, room_name, message, attachment, attachment_name):
    receiver = User.objects.get(id=receiver_id)
    return ChatMessage.objects.create(
        sender=sender,
        receiver=receiver,
        room_name=room_name,
        message=message,
        attachment=attachment,
        attachment_name=attachment_name
    )

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']  # e.g., "14-15"
        self.room_group_name = f'chat_{self.room_name}'

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get('message')
        sender_id = data.get('sender_id')
        sender_name = data.get('sender_name')
        receiver_id = data.get('receiver_id')
        attachment = data.get('attachment')
        attachment_name = data.get('attachment_name')

        print(f"Message: {message}, Sender: {sender_name}, Receiver: {receiver_id}, Attachment: {attachment_name}")

        sender = await get_user(sender_id)

        # Save message to database
        await save_message(
            sender=sender,
            receiver_id=receiver_id,
            room_name=self.room_name,
            message=message,
            attachment=attachment,
            attachment_name=attachment_name
        )

        # Broadcast to all clients in the group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender_id': sender_id,
                'sender_name': sender_name,
                'receiver_id': receiver_id,
                'attachment': attachment,
                'attachment_name': attachment_name,
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'message': event.get('message'),
            'sender_id': event.get('sender_id'),
            'sender_name': event.get('sender_name'),
            'receiver_id': event.get('receiver_id'),
            'attachment': event.get('attachment'),
            'attachment_name': event.get('attachment_name'),
        }))
