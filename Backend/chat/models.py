from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()



class Contact(models.Model):
    user = models.ForeignKey(
        User, related_name='contact', on_delete=models.CASCADE)
    friends = models.ManyToManyField(User, related_name='contacts', blank=True)

    def __str__(self):
        return self.user.username


class Conversation(models.Model):
    participants = models.ManyToManyField(
        User, related_name='conversations', blank=True, through='UserConversation')
    is_private = models.BooleanField(default=True)
    title = models.CharField(max_length=1000)


    def __str__(self):
        return "{}".format(self.pk)

    def get_last_messages(self, start, count):
        return self.messages.order_by('-timestamp').all()[start:start+count]

    def get_last_messages_timestamp(self, timestamp):
        return self.messages.order_by('-timestamp').filter(timestamp__gt=timestamp)


class Message(models.Model):
    author = models.ForeignKey(
        User, related_name='messages', on_delete=models.CASCADE)
    conversation = models.ForeignKey(
        Conversation, related_name='messages', on_delete=models.CASCADE, null=True)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.author.username

class UserConversation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE)

    unread = models.BooleanField(default=False)
    last_read_timestamp = models.DateTimeField(auto_now_add=True)

    def get_unread(self):
        if not self.unread:
            return []
        return self.conversation.get_last_messages_timestamp(self.last_read_timestamp)

    def count_unread(self):
        return len(self.get_unread())

    def title(self):
        return self.conversation.title



