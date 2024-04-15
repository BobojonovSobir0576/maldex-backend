from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from apps.user.models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'is_staff')
    readonly_fields = ('last_login', 'date_joined')
    ordering = ['email']
    fieldsets = (
        (None, {'fields': ('email', 'first_name', 'last_name', 'image')}),
        ('Extra informations', {'fields': ('password', 'last_login', 'date_joined')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'image', 'password1', 'password2'),
        }),
    )
