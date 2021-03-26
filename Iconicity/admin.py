from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(UserProfile)
admin.site.register(Like)
admin.site.register(Comment)
admin.site.register(FriendRequest)
admin.site.register(Post)
admin.site.register(Inbox)
admin.site.register(ExternalServer)


class SignUpConfirmAdmin(admin.ModelAdmin):
    list_display = ('boolean',)
    def has_add_permission(self, request):
        return False

admin.site.register(SignUpConfirm, SignUpConfirmAdmin)
