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
    if not Conversation.objects.filter(title=f"{user.username}, {friend.username}", 
                                        is_private=True
                                        ).exists():
        print(f"accepted and create new conw")
        conversation = Conversation.objects.create(title=f"{user.username}, {friend.username}")
        conversation.save()
        add_user_to_conversation(user, conversation)
        add_user_to_conversation(friend, conversation)
    request.delete()
    return True
  except Exception as e:
    print(e)
    return False

def reject_friend(request: FriendRequest):
  request.delete()


# def search_users()