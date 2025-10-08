import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import PendingTransaction

class TransactionConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("transactions", self.channel_name)
        await self.accept()
        # send initial 10 transactions
        await self.send_transactions()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("transactions", self.channel_name)

    @database_sync_to_async
    def get_transactions(self):
        txns = PendingTransaction.objects.all().order_by('-timestamp')[:10]
        # print(txns)
        return [
            {
                'hash': t.hash,
                'amount': str(t.amount),
                'timestamp': t.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            }
            for t in txns
        ]

    async def send_transactions(self):
        data = await self.get_transactions()
        await self.send(text_data=json.dumps({'transactions': data}))

    async def transaction_update(self, event):
        await self.send_transactions()


# A simple test consumer for debugging purposes

class TestConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print("TEST: WebSocket connect called")
        await self.accept()
        await self.send(text_data=json.dumps({
            'message': 'Connected successfully!'
        }))
        print("TEST: Connection accepted and message sent")

    async def disconnect(self, close_code):
        print(f"TEST: WebSocket disconnected: {close_code}")

    async def receive(self, text_data):
        print(f"TEST: Received: {text_data}")