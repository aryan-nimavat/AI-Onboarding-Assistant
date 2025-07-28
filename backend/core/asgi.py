# core/asgi.py
import os
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack # For user authentication in WebSockets
from django.core.asgi import get_asgi_application
import agents.routing # Your app's WebSocket routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack( # For user authentication
        URLRouter(
            agents.routing.websocket_urlpatterns # Your WebSocket URL patterns
        )
    ),
})