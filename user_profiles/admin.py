from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from .models import Access, UserProfile, UserIpAddress


@admin.register(Access)
class AccessAdmin(admin.ModelAdmin):
    list_display = ('userprofile', 'control', 'access_type')
    list_filter = ('userprofile', 'control', 'access_type')
    search_fields = ('userprofile__user__username', 'userprofile__user__email')


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'profile_type', 'send_files_report')
    filter = 'profile_type'
    raw_id_fields = ('user',)
    search_fields = ('user__username', 'user__email')


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile Utilisateurs'


class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('id', 'email', 'first_name', 'last_name', 'is_staff', 'date_joined')
    filter = 'profile__profile_type'

@admin.register(UserIpAddress)
class UserIpAddress(admin.ModelAdmin):
    model = UserIpAddress
    list_display = ('id', 'ip', 'username', 'created_at')

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
