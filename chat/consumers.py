import json
from channels.generic.websocket import AsyncWebsocketConsumer

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
        attachment = data.get('attachment')  # 👈 base64 URL or blob URL
        attachment_name = data.get('attachment_name')

        print(f"Message: {message}, Sender: {sender_name}, Receiver: {receiver_id}, Attachment: {attachment_name}")

        # Broadcast message with attachment if available
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
