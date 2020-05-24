# chat/consumers.py
import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncWebsocketConsumer, WebsocketConsumer
from .serializers import MessageSerializer
from .utils import create_message, create_friend_request, accept_friend
from .models import Conversation, UserConversation, FriendRequest
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
        elif type == 'key_request':
            print('GOT KEY REQUEST')
            conversation_id = text_data_json['conversation_id']
            dh_key =  text_data_json['dh_key']

            conversation = Conversation.objects.get(pk=conversation_id)
            if conversation:
                userConversation = UserConversation.objects.get(user=self.user, conversation=conversation)
                if userConversation: #sender of a request is a member of the conversation, notify admin
                    room_group_name = 'chat_%s' % conversation.admin.pk
                    async_to_sync(self.channel_layer.group_send)(
                        room_group_name,
                        {
                            'type': 'key_request',
                            'conversation_id': conversation_id,
                            'dh_key': str(dh_key),
                            'user_id': self.user.pk
                        }
                    )
        elif type == 'key_response':
            print('GOT KEY RESPONSE')
            #get message from conversation admin, and redirect it to its proper receiver
            conversation_id = text_data_json['conversation_id']
            user_id = text_data_json['user_id']
            dh_key = text_data_json['dh_key']
            rsa_key = text_data_json['rsa_key']

            room_group_name = 'chat_%s' % user_id
            async_to_sync(self.channel_layer.group_send)(
                room_group_name,
                {
                    'type': 'key_response',
                    'user_id': user_id,
                    'conversation_id': conversation_id,
                    'dh_key': str(dh_key),
                    'rsa_key': rsa_key
                }
            )
        elif type == 'invite_friend':
            friend_username = text_data_json['friend']

            receiver = User.objects.get(username=friend_username)
            notifications = receiver.notifications.get()
            # if friend request was not already sent
            if not FriendRequest.objects.filter(user=notifications,
                                                sender=self.user.username).exists():
                notifications = receiver.notifications.get()
                request = create_friend_request(notifications, self.user)
                room_group_name = f'chat_{self.user.pk}'
                async_to_sync(self.channel_layer.group_send)(
                room_group_name,
                {
                    'type': 'invite',
                    'sender_name': self.user.username,
                    'request_id': request.id,
                    'timestamp': str(request.timestamp)
                }
            )

        elif type == 'accept friend':
            request_id = text_data_json['id']
            f_request = FriendRequest.objects.get(id=request_id)
            accept_friend(self.user, f_request.sender, f_request)
            room_group_name = f'chat_{f_request.sender.username}'
            async_to_sync(self.channel_layer.group_send)(
                room_group_name,
                {
                    'type': 'accepted_req_notify',
                    'sender_name': self.user.username,
                }
            )
            


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

    def key_request(self, event):
        conversation_id = event['conversation_id']
        dh_key = event['dh_key']
        user_id = event['user_id']
        async_to_sync(self.send(text_data=json.dumps({
            'type': 'key_request',
            'conversation_id': conversation_id,
            'dh_key': dh_key,
            'user_id': user_id
        })))

    def key_response(self, event):
        user_id = event['user_id']
        conversation_id = event['conversation_id']
        dh_key = event['dh_key']
        rsa_key = event['rsa_key']
        async_to_sync(self.send(text_data=json.dumps({
            'type': 'key_response',
            'user_id': user_id, 
            'conversation_id': conversation_id,
            'dh_key': dh_key,
            'rsa_key': rsa_key
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

    def invite(self, event):
        request_id = event['request_id']
        sender = event['sender']
        timestamp = event['timestamp']
        async_to_sync(self.send(text_data=json.dumps({
            'type': 'friend_request',
            'sender': sender,
            'request_id': request_id,
            'timestamp': timestamp
        })))

    def accepted_req_notify(self, event):
        sender = event['sender_name']
        async_to_sync(self.send(text_data=json.dumps({
            'type': 'accepted_f_request',
            'sender': sender
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