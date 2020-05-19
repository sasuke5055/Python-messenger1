from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import User, Contact, Conversation, UserConversation, FriendRequest, Notifications
import json
from django.core import serializers
from .serializers import ContactSerializer, UserSerializer, UserConversationSerializer, MessageSerializer, FriendRequestsSerializer
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from .utils import create_friend_request, accept_friend, reject_friend

def index(request):
    return render(request, 'chat/index.html')

def room(request):
    return render(request, 'chat/room.html', {
        
    })

class ContactsView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        content = {'content': ContactSerializer(request.user.contact.get()).data}
        return Response(content)

    def post(self, request):
        if request.data['type'] == 'delete friend':
            try:
                friend = User.objects.get(username=request.data['username'])
                request.user.contact.get().friends.remove(friend)
                friend.contact.get().friends.remove(request.user)
                return Response({'content': True})
            except Exception as e:
                print(e)
                return Response({'content': False})

class ConversationsView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        conversations_data = []
        for conversation in request.user.conversations.all():
             conversations_data.append(UserConversation.objects.get(user=request.user, conversation=conversation))
        content = {'content': UserConversationSerializer(conversations_data, many=True).data}
        return Response(content)


class ConversationMessagesView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk):
        conversation = Conversation.objects.get(id=pk)
        content = {'content':MessageSerializer(conversation.get_last_messages(0,20), many=True).data}
        return Response(content)

class CustomObtainAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        response = super(CustomObtainAuthToken, self).post(request, *args, **kwargs)
        token = Token.objects.get(key=response.data['token'])
        return Response({'token': token.key, 'user_id': token.user_id})


class NotificationsView(APIView):
    permission_classes = (IsAuthenticated, )

    def post(self, request):

        # handle friend invitation
        if request.data['type'] == 'invite friend':
            try:
                receiver = User.objects.get(username=request.data['friend'])
                notifications = receiver.notifications.get()
                # if friend request was not already sent
                if not FriendRequest.objects.filter(user=notifications,
                                                 sender=request.user).exists():
                    notifications = receiver.notifications.get()
                    create_friend_request(notifications, request.user)
                    return Response({'content': 'success'})
                else:
                    return Response({'content': 'already invited'})
            except Exception as e:
                print(e)
                return Response({'content': 'error'})
        
        # handle accepting friend request
        elif request.data['type'] == 'accept friend':
            try:
                friend_request = FriendRequest.objects.get(id=request.data['id'])
                accept_friend(request.user, friend_request.sender, friend_request)
                return Response({'content': True})
            except Exception as e:
                print(e)
                return Response({'content': False})

        # handle rejecting friend request
        elif request.data['type'] == 'reject friend':
            try:
                friend_request = FriendRequest.objects.get(id=request.data['id'])
                reject_friend(friend_request)
                return Response({'content': True})
            except Exception as e:
                print(e)
                return Response({'content': False})

    # return all user friend requests
    def get(self, request):
        notifications = request.user.notifications.get()
        content = {'content':  FriendRequestsSerializer(notifications.get_all_notifications(), many=True).data}
        return Response(content)
    