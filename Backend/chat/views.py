from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import User, Contact, Conversation, UserConversation
import json
from django.core import serializers
from .serializers import ContactSerializer, UserSerializer, UserConversationSerializer, MessageSerializer
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
        print("XD1", request.data['start'])
        print("XD2",request.data['end'])
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