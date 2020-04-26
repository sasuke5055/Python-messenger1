from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()



class Contact(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE)
    friends = models.ManyToManyField('self', related_name='friends', blank=True)

    def __str__(self):
        return self.user.username


class Conversation(models.Model):
    participants = models.ManyToManyField(
        Contact, related_name='chats', blank=True)
    is_private = models.BooleanField(default=True)
    title = models.CharField()
    #colors etc

    def __str__(self):
        return "{}".format(self.pk)

    def get_last_messages(self, start, count):
        return self.messages.order_by('-timestamp').all()[start:start+count]

    def get_last_messages_timestamp(self, timestamp):
        return self.messages.order_by('-timestamp').filter(timestamp__gt=timestamp)


class Message(models.Model):
    author = models.ForeignKey(
        Contact, related_name='messages', on_delete=models.CASCADE)
    conversation = models.ForeignKey(
        Conversation, related_name='messages', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.contact.user.username


class UserConversation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE)

    unread = models.BooleanField(default=False, on_delete=models.CASCADE)
    last_read_timestamp = models.DateTimeField(auto_now_add=True)

    def get_unread(self):
        if not self.unread:
            return []
        return self.conversation.get_last_messages_timestamp(self.last_read_timestamp)

    def count_unread(self):
        return len(self.get_unread())



