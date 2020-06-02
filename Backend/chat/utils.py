from .models import *

def create_message(author, conversation, content):
  try:
    new_message = Message.objects.create(author=author, content=content, conversation=conversation)

    for participant in conversation.participants.all():
      userConversation = UserConversation.objects.get(user=participant, conversation=conversation)
      userConversation.unread = True
    new_message.save()
    return new_message

  except Exception as e:
    print(e)
    return None
  
def add_user_to_conversation(user, conversation):
  conversation.participants.add(user)
  user_conversation = UserConversation.objects.get_or_create(user=user, conversation=conversation)
  conversation.save()
  return user_conversation[0]


def create_friend_request(notifications_set: Notifications, sender: User):
  try:
    new_request = FriendRequest(user=notifications_set, sender=sender, sender_name=sender.username)

    notifications_set.unseen = True
    new_request.save()

    return new_request

  except Exception as e:
    print(e)
    return None


def accept_friend(user: User, friend: User, request: FriendRequest):
  try:
    user.contact.get().friends.add(friend)
    friend.contact.get().friends.add(user)
    user.save()
    friend.save()
    # check if that two users were friends in past
    title=f"{user.username}, {friend.username}"
    conversation = create_new_conversation(title, user) 
    if conversation is not None:
      add_user_to_conversation(friend, conversation)
    request.delete()
    return conversation
  except Exception as e:
    print(e)
    return None

def create_new_conversation(title, admin : User, typ=True):
  if not Conversation.objects.filter(title=title,
                                   is_private=typ
                                   ).exists():
      print(f"accepted and create new conv")
      conversation = Conversation.objects.create(title=title, admin=admin)
      conversation.save()
      add_user_to_conversation(admin, conversation)
      return conversation
  return None


def reject_friend(request: FriendRequest):
  request.delete()