# asgi.py
import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import chat.routing  # Ensure you're importing the correct routing module

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_channel.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(), # Reference to your Http URL patterns
    "websocket": AuthMiddlewareStack(  # Ensure AuthMiddlewareStack is used for authentication
        URLRouter(
            chat.routing.websocket_urlpatterns  # Reference to your WebSocket URL patterns
        )
    ),
})
