from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import User, Contact, Conversation, UserConversation
import json
from django.core import serializers
from .serializers import ContactSerializer, UserSerializer, UserConversationSerializer, MessageSerializer, FriendRequestsSerializer
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token

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
        start = int(request.data['start'])
        end = int(request.data['end'])
        conversation = Conversation.objects.get(id=pk)
        content = {'content':MessageSerializer(conversation.get_last_messages(start,end), many=True).data}
        return Response(content)

class CustomObtainAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        response = super(CustomObtainAuthToken, self).post(request, *args, **kwargs)
        token = Token.objects.get(key=response.data['token'])
        return Response({'token': token.key, 'user_id': token.user_id})


class SearchView(APIView):
    permission_classes = (IsAuthenticated,)

    # return users who's username contains key
    def get(self, request):
        key = request.data['key']

        matching_friends = request.user.contact.get().friends.filter(username__icontains=key)
        friends = [x.username for x in matching_friends]
        # getting users who are not your friends
        users = User.objects.filter(username__icontains=key).exclude(username__in=friends).exclude(pk=request.user.pk)
        matching_friends = UserSerializer(matching_friends, many=True).data
        strangers = UserSerializer(users, many=True).data
        content = {'content': matching_friends + strangers}
        return Response(content)

class NotificationsView(APIView):
    permission_classes = (IsAuthenticated, )

    # return all user friend requests
    def get(self, request):
        notifications = request.user.notifications.get()
        content = {'content':  FriendRequestsSerializer(notifications.get_all_notifications(), many=True).data}
        return Response(content)


class PasswordChangeView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        new_password = request.data['new_passw']
        request.user.set_password(new_password)
        request.user.save()
        return Response({'content': True})
