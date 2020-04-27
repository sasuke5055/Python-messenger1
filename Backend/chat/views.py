from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import User, Contact, Conversation, UserConversation
import json
from django.core import serializers
from .serializers import ContactSerializer, UserSerializer, UserConversationSerializer, MessageSerializer

def index(request):
    return render(request, 'chat/index.html')

def room(request, room_name):
    return render(request, 'chat/room.html', {
        'room_name': room_name
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
        conversation = Conversation.objects.get(id=pk)
        content = {'content':MessageSerializer(conversation.get_last_messages(0,20), many=True).data}
        return Response(content)