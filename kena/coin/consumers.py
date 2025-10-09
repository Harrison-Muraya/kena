import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import PendingTransaction

# Consumer to handle WebSocket connections for real-time transaction updates
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
        txns_qs  = PendingTransaction.objects.all().order_by('-timestamp')
        txnsCount = txns_qs.count()
        txns = txns_qs[:4]
        return {
            'count': txnsCount,
            'list': [
                {
                    'hash': t.hash,
                    'amount': str(t.amount),
                    'timestamp': t.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                }
                for t in txns
            ]
        }

    async def send_transactions(self):
        data = await self.get_transactions()
        await self.send(text_data=json.dumps({'transactions': data['list'], 'count': data['count']}))

    async def transaction_update(self, event):
        await self.send_transactions()


# Consumer to handle WebSocket connections for real-time blocks updates
class BlockConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("blocks", self.channel_name)
        await self.accept()
        # send initial 10 blocks
        await self.send_blocks()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("blocks", self.channel_name)

    @database_sync_to_async
    def get_blocks(self):
        from .models import Block  # Import here to avoid circular import
        blocks = Block.objects.all().order_by('-timestamp')[:4]
        # print(blocks)
        return [
            {
                'height': b.height,
                'hash': b.hash,
                'previous_hash': b.previous_hash,
                'timestamp': b.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'transactions': b.transactions,
            }
            for b in blocks
        ]

    async def send_blocks(self):
        data = await self.get_blocks()
        await self.send(text_data=json.dumps({'blocks': data}))

    async def block_update(self, event):
        await self.send_blocks()

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