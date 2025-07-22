"""
ASGI config for core project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# This is for HTTP requests (your Django REST Framework APIs)
application = get_asgi_application()

# We'll add WebSocket routing here in a later week
# application = ProtocolTypeRouter({
#     "http": get_asgi_application(),
#     "websocket": URLRouter(
#         # Your WebSocket URL patterns will go here
#     ),
# })
