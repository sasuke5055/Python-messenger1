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

