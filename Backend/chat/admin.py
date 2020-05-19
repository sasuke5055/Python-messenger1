from django.contrib import admin
from .models import *
 
class UserConversationAdmin(admin.ModelAdmin):
    readonly_fields = ('last_read_timestamp',)
 
# Register your models here.
admin.site.register(Contact)
admin.site.register(Message)
admin.site.register(UserConversation, UserConversationAdmin)
admin.site.register(Conversation)
admin.site.register(Notifications)
admin.site.register(FriendRequest)