from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/test/$', consumers.TestConsumer.as_asgi()),
    re_path(r'ws/transactions/$', consumers.TransactionConsumer.as_asgi()),
    re_path(r'ws/blocks/$', consumers.BlockConsumer.as_asgi()),
]
