# chat/consumers.py

import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncWebsocketConsumer, WebsocketConsumer
from .serializers import MessageSerializer
from .utils import create_message, create_friend_request, accept_friend, reject_friend, create_new_conversation, add_user_to_conversation
from .models import Conversation, UserConversation, FriendRequest, User
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
        print('cokolwiek')
        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        print("kurwa wchodze")
        print(text_data)
        text_data_json = json.loads(text_data)
        print(text_data_json)

        type = text_data_json['type']
        if type == 'message':
            content = text_data_json['content']
            conversation_id = text_data_json['conversation_id']
            conversation = Conversation.objects.get(pk=conversation_id)
            print(self.user, conversation, content)
            message = create_message(self.user, conversation, content)
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
            conversation = Conversation.objects.get(pk=conversation_id)
            userConversation = UserConversation.objects.get(user=self.user, conversation=conversation)
            userConversation.is_listening = True
            #TODO: add closing conversation
            userConversation.save()
        elif type == 'key_request':
            print('GOT KEY REQUEST')
            conversation_id = text_data_json['conversation_id']
            dh_key = text_data_json['dh_key']

            conversation = Conversation.objects.get(pk=conversation_id)
            if conversation:
                userConversation = UserConversation.objects.get(user=self.user, conversation=conversation)
                if userConversation:  # sender of a request is a member of the conversation, notify admin
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
            # get message from conversation admin, and redirect it to its proper receiver
            conversation_id = text_data_json['conversation_id']
            user_id = text_data_json['user_id']
            dh_key = text_data_json['dh_key']
            rsa_key = text_data_json['rsa_key']
            flag = text_data_json['flag']

            room_group_name = 'chat_%s' % user_id
            async_to_sync(self.channel_layer.group_send)(
                room_group_name,
                {
                    'type': 'key_response',
                    'user_id': user_id,
                    'conversation_id': conversation_id,
                    'dh_key': str(dh_key),
                    'rsa_key': rsa_key,
                    'flag': flag,
                }
            )
        elif type == 'invite_friend':
            print('wchodze do invitefr')
            friend_id = text_data_json['friend_id']
            friend_id = int(friend_id)
            receiver = User.objects.get(pk=friend_id)
            print(receiver)
            notifications = receiver.notifications.get()
            # if friend request was not already sent,2
            print(receiver)
            # todo: here changed
            if not FriendRequest.objects.filter(user=notifications,
                                                sender=self.user).exists():
                notifications = receiver.notifications.get()
                print(receiver)
            print('dupaduap')
            request = create_friend_request(notifications, self.user)
            room_group_name = f'chat_{friend_id}'
            async_to_sync(self.channel_layer.group_send)(
                room_group_name,
                {
                    'type': 'invite',
                    'sender_name': self.user.username,
                    'request_id': request.id,
                    'timestamp': str(request.timestamp)
                }
            )

        elif type == 'response_friend_req':
            request_id = text_data_json['id']
            response = text_data_json['response']
            f_request = FriendRequest.objects.get(id=request_id)
            if response == 'True':
                conversation = accept_friend(self.user, f_request.sender, f_request)
                if conversation is not None:
                    self.notify_conversation_admin(conversation) #TA LINIJKA JEST WAŻNA / VERY IMPORTANT LINE 
            elif response == "False":
                reject_friend(f_request)
            room_group_name = f'chat_{f_request.sender.id}'
            async_to_sync(self.channel_layer.group_send)(
                room_group_name,
                {
                    'type': 'response_req_notify',
                    'sender_name': self.user.username,
                    'response': response,
                }
            )
        elif type == 'create_group':
            title = text_data_json['title']
            admin_id = int(text_data_json['admin_id'])
            users = text_data_json['users_ids']
            admin = User.objects.get(pk=admin_id)
            conv = create_new_conversation(title, admin, False)
            self.notify_conversation_admin(conv)
            for user_id in users:
                user = User.objects.get(pk=int(user_id))
                add_user_to_conversation(user, conv)

                room_group_name = f'chat_{int(user_id)}'
                async_to_sync(self.channel_layer.group_send)(
                    room_group_name,
                    {
                        'type': 'created_group_notify',
                        'title': title,
                        'admin_name': admin.username,
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
        flag = event['flag']
        async_to_sync(self.send(text_data=json.dumps({
            'type': 'key_response',
            'user_id': user_id,
            'conversation_id': conversation_id,
            'dh_key': dh_key,
            'rsa_key': rsa_key,
            'flag': flag,
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
        sender = event['sender_name']
        timestamp = event['timestamp']
        async_to_sync(self.send(text_data=json.dumps({
            'type': 'friend_request',
            'sender': sender,
            'request_id': request_id,
            'timestamp': timestamp
        })))

    def response_req_notify(self, event):
        sender = event['sender_name']
        response = event['response']
        async_to_sync(self.send(text_data=json.dumps({
            'type': 'response_f_request',
            'sender': sender,
            'response': response,
        })))

    def notify_conversation_admin(self, conversation : Conversation):
        room_group_name = f'chat_{conversation.admin.pk}'
        async_to_sync(self.channel_layer.group_send)(
            room_group_name,
            {
                'type': 'new_conversation',
                'conversation_id': conversation.id,
            }
        )
    def new_conversation(self,event):
        conversation_id = event['conversation_id']
        async_to_sync(self.send(text_data=json.dumps({
            'type': 'new_conversation',
            'conversation_id': conversation_id,
        })))

    def created_group_notify(self, event):
        title = event['title']
        admin_name = event['admin_name']
        async_to_sync(self.send(text_data=json.dumps({
            'type': 'create_group_notify',
            'title': title,
            'admin': admin_name,
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
