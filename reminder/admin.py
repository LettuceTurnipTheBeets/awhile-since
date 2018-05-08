from django.contrib import admin
from .models import UserProfile, Task
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from reminder.models import UserProfile

class UserProfileInline(admin.StackedInline):
    """Define an inline admin descriptor for Employee model which acts a bit
       like a singleton
    """
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'userprofile'

"""Define a new User admin"""
class UserAdmin(UserAdmin):
    inlines = (UserProfileInline, )

"""Re-register UserAdmin"""
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

admin.site.register(UserProfile)
admin.site.register(Task)
