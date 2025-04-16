import json
from channels.generic.websocket import AsyncWebsocketConsumer

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Extract room name from URL (e.g., '14-15' -> chat_14-15)
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        print(f"Connecting to room: {self.room_group_name}")

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        # Accept the WebSocket connection
        await self.accept()
        print(f"Connection accepted for room: {self.room_group_name}")

    async def disconnect(self, close_code):
        print(f"Disconnecting from room: {self.room_group_name}, code: {close_code}")

        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        # Receive message from WebSocket
        data = json.loads(text_data)
        message = data.get('message')
        sender_id = data.get('sender_id')
        sender_name = data.get('sender_name')

        print(f"Message received: {message} from {sender_id} - {sender_name}")

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender_id': sender_id,
                'sender_name': sender_name
            }
        )

    async def chat_message(self, event):
        # Send message to WebSocket
        print(f"Sending message: {event['message']} to room: {self.room_group_name}")

        await self.send(text_data=json.dumps({
            'message': event['message'],
            'sender_id': event['sender_id']
        }))
