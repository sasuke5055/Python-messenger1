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
  
  

