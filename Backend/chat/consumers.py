# chat/consumers.py
import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncWebsocketConsumer, WebsocketConsumer
from .serializers import MessageSerializer
from .utils import create_message
from .models import Conversation, UserConversation
from rest_framework.authtoken.models import Token


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        try:
            headers = dict(self.scope['headers'])
            if b'authorization' in headers:
                token_name, token_key = headers[b'authorization'].decode().split()
                if token_name == 'Token':
                    token = Token.objects.get(key=token_key)
                    self.scope['user'] = token.user
                    self.user = token.user
            
            print('GITARA', self.user)
        except Exception as e:
            print(e)
            self.user = self.scope['user']
            print('PRZEGLADARKA', self.user)

        self.room_group_name = 'chat_%s' % self.user.pk
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        type = text_data_json['type']
        if type == 'message':
            content = text_data_json['content']
            conversation_id = text_data_json['conversation_id']
            conversation = Conversation.objects.get(pk=conversation_id)
            print(self.user, conversation, content)
            message = create_message(self.user ,conversation, content)
            author = self.user.pk
            for user in conversation.participants.all():
                userConversation = UserConversation.objects.get(user=user, conversation=conversation)
                if userConversation.is_listening:
                    room_group_name = 'chat_%s' % user.pk
                    output_dict = MessageSerializer(message).data
                    output_dict['conversation_id'] = conversation_id
                    output_dict['type'] = 'message'

                    async_to_sync(self.channel_layer.group_send)(
                        room_group_name,
                        output_dict
                    )
                else:
                    room_group_name = 'chat_%s' % user.pk
                    async_to_sync(self.channel_layer.group_send)(
                        room_group_name,
                        {
                            'type': 'notify',
                            'conversation_id': conversation_id
                        }
                    )
        elif type == 'join_conversation':
            conversation_id = text_data_json['conversation_id']
            conversation = Conversation.objects.get(pk = conversation_id)
            userConversation = UserConversation.objects.get(user=self.user, conversation=conversation)
            userConversation.is_listening = not userConversation.is_listening
            userConversation.save()
            #TODO - add close convesation

    # Receive message from room group
    def chat_message(self, event):
        message = event['message']
        async_to_sync(self.send(text_data=json.dumps({
            'message': message
        })))
    
    def notify(self, event):
        conversation_id = event['conversation_id']
        async_to_sync(self.send(text_data=json.dumps({
            'type': 'new_notification',
            'conversation_id': conversation_id
        })))
    
    def message(self, event):
        content = event['content']
        conversation_id = event['conversation_id']
        author = event['author']
        timestamp = event['timestamp']
        async_to_sync(self.send(text_data=json.dumps({
            'type': 'new_message',
            'conversation_id': conversation_id,
            'author': author,
            'timestamp': timestamp,
            'content': content
        })))

# class ChatConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         self.room_name = self.scope['url_route']['kwargs']['room_name']
#         self.room_group_name = 'chat_%s' % self.room_name

#         # Join room group
#         await self.channel_layer.group_add(
#             self.room_group_name,
#             self.channel_name
#         )

#         await self.accept()

#     async def disconnect(self, close_code):
#         # Leave room group
#         await self.channel_layer.group_discard(
#             self.room_group_name,
#             self.channel_name
#         )

#     # Receive message from WebSocket
#     async def receive(self, text_data):
#         text_data_json = json.loads(text_data)
#         message = text_data_json['message']

#         # Send message to room group
#         await self.channel_layer.group_send(
#             self.room_group_name,
#             {
#                 'type': 'chat_message',
#                 'message': message
#             }
#         )

#     # Receive message from room group
#     async def chat_message(self, event):
#         message = event['message']

#         # Send message to WebSocket
#         await self.send(text_data=json.dumps({
#             'message': message
#         }))