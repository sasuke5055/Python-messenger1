from django.urls import re_path

from .consumers import ChatConsumer

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<room_name>\w+)/$', ChatConsumer),
#     re_path('chat/aaa/', ChatConsumer),
]

# application = ProtocolTypeRouter({

#     "websocket": AuthMiddlewareStack(
#         URLRouter([
#             re_path(r'ws/chat/(?P<room_name>\w+)/$', ChatConsumer),
#         ])
#     ),

# })