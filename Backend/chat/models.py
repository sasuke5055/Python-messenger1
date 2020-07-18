from django.db import models
from django.contrib.auth import get_user_model
from django.dispatch import receiver
from allauth.account.signals import user_signed_up

User = get_user_model()


# executes when new user signed up
@receiver(user_signed_up)
def after_user_signed_up(request, user, **kwargs):
    # create contact model after registration
    Contact.objects.create(user=user)

    # create notifications model after registration
    Notifications.objects.create(user=user)


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
    admin = models.ForeignKey(User, default=None, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return "{}: {}".format(self.pk, self.title)

    def get_last_messages(self, start, count):
        return self.messages.order_by('-timestamp').all()[start:start + count]

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
        return "author:{}, conversation: {}, id: {}".format(self.author.username, self.conversation, self.pk)


class UserConversation(models.Model):
    readonly_fields = ('last_read_timestamp',)

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE)

    unread = models.BooleanField(default=False)
    last_read_timestamp = models.DateTimeField(auto_now_add=True)
    is_listening = models.BooleanField(default=True)

    def get_unread(self):
        if not self.unread:
            return []
        return self.conversation.get_last_messages_timestamp(self.last_read_timestamp)

    def count_unread(self):
        return len(self.get_unread())

    def title(self):
        return self.conversation.title

    def __str__(self):
        return "{} conversation: {}".format(self.user, self.conversation)


class Notifications(models.Model):
    user = models.ForeignKey(User, related_name='notifications', on_delete=models.CASCADE)

    unseen = models.BooleanField(default=False)
    last_seen_timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notifications of {self.user.username}"

    def get_all_notifications(self):
        return self.receiver.order_by('-timestamp').all()

    def get_last_notifications_timestamp(self, timestamp):
        return self.receiver.order_by('-timestamp').filter(timestamp__gt=timestamp)

    def get_unseen(self):
        if not self.unseen:
            return []
        else:
            return self.get_last_notifications_timestamp(self.last_seen_timestamp)

    def count_unread(self):
        return len(self.get_unseen())


class FriendRequest(models.Model):
    user = models.ForeignKey(Notifications, related_name='receiver', on_delete=models.CASCADE)
    sender = models.ForeignKey(User, related_name='sender', on_delete=models.CASCADE)
    sender_name = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)
    notify_type = models.CharField(max_length=20, blank=True)

    if User == sender:
        notify_type = 'request invite'
    else:
        notify_type = 'request accept'

    def __str__(self):
        return f"type: {self.notify_type}, from: {self.sender}, to: {self.user.user}"
