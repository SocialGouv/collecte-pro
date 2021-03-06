from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from .models import UserProfile, UserIpAddress


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'profile_type', 'send_files_report')
    list_filter = ('profile_type', 'controls')
    raw_id_fields = ('user',)
    filter_horizontal = ('controls',)
    search_fields = ('user__username', 'user__email')


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile Utilisateurs'
    filter_horizontal = ('controls',)


class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('id', 'email', 'first_name', 'last_name', 'is_staff', 'date_joined')
    list_filter = ('profile__profile_type', 'profile__controls')

@admin.register(UserIpAddress)
class UserIpAddress(admin.ModelAdmin):
    model = UserIpAddress
    list_display = ('id', 'ip', 'username', 'created_at')

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
