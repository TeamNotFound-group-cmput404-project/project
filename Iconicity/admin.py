from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(UserProfile)
admin.site.register(LikeSingle)
admin.site.register(Comment)
admin.site.register(FriendRequest)
admin.site.register(Post)

admin.site.register(Inbox)
