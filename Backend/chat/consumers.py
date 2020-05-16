# chat/consumers.py
import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncWebsocketConsumer, WebsocketConsumer
from .utils import create_message
from .models import Conversation, UserConversation
from rest_framework.authtoken.models import Token


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        token_id = str(self.scope['headers'][-1][1]).split(' ')[-1][:-1]
        token = Token.objects.get(pk=token_id)
        self.user = token.user

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
        print('NEW MESSAGE, ', type)
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
                    async_to_sync(self.channel_layer.group_send)(
                        room_group_name,
                        {
                            'type': 'message',
                            'conversation_id': conversation_id,
                            'author': author,
                            'timestamp': str(message.timestamp),
                            'content': content
                        }
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
            #TODO - add close conversation

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