import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Transaction, Message, User

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.transaction_id = self.scope['url_route']['kwargs']['transaction_id']
        self.room_group_name = f'chat_{self.transaction_id}'
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_content = data['message']
        user = self.scope['user']
        await self.save_message(user.username, self.transaction_id, message_content)
        await self.channel_layer.group_send(
            self.room_group_name,
            {'type': 'chat_message', 'message': message_content, 'sender': user.username}
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'sender': event['sender'],
            'file_url': event.get('file_url'),
            'is_image': event.get('is_image')
        }))

    @database_sync_to_async
    def save_message(self, username, transaction_id, content):
        sender = User.objects.get(username=username)
        tx = Transaction.objects.get(id=transaction_id)
        return Message.objects.create(transaction=tx, sender=sender, content=content)

class TradingFloorConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = 'trading_floor'
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
    async def service_message(self, event):
        await self.send(text_data=json.dumps({'message': event['message']}))

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user_id = self.scope['user'].id
        self.group_name = f'user_{self.user_id}_notifications'
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
    async def send_notification(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'target_url': event.get('target_url', '#')
        }))