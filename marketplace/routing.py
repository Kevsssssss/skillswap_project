from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/trading-floor/', consumers.TradingFloorConsumer.as_asgi()),
    path('ws/chat/<int:transaction_id>/', consumers.ChatConsumer.as_asgi()),
    path('ws/notifications/', consumers.NotificationConsumer.as_asgi()),
]