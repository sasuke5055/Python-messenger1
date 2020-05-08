from rest_framework import serializers
from .models import Contact, User, UserConversation, Conversation, Message

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']


class ContactSerializer(serializers.ModelSerializer):
    friends = UserSerializer(many=True, read_only=True)

    class Meta:
        model = Contact
        fields = ['user', 'friends']



class UserConversationSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField('get_conversation_id')
    class Meta:
        model = UserConversation
        fields = ['id', 'title', 'count_unread']

    def get_conversation_id(self, obj):
        return obj.conversation.pk


class MessageSerializer(serializers.ModelSerializer):
    author = UserSerializer()
    class Meta:
        model = Message
        fields = ['content', 'timestamp', 'author']