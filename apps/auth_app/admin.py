from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from import_export.admin import ImportExportModelAdmin
from django.contrib.auth.models import Group

from apps.auth_app.models import CustomUser, UserLastLogin


class NewUser(ImportExportModelAdmin, UserAdmin):
    model = CustomUser
    list_display = ['email', 'phone', 'username', 'is_active', 'is_staff', 'id']
    search_fields = ['email', 'phone', 'groups', 'username']
    ordering = ['email', 'username']
    fieldsets = (
        (None, {'fields': ('first_name', 'last_name', 'email', 'phone', 'password')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser',
                                    'groups')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('Personal Information',
         {'fields': ('date_of_birth', 'photo', 'about', 'gender')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2'),
        }),
    )


class UserLastLoginAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ['user', 'login_time', 'id']
    search_fields = ['user__username']


admin.site.register(CustomUser, NewUser)
# admin.site.register(UserLastLogin, UserLastLoginAdmin)
admin.site.unregister(Group)
