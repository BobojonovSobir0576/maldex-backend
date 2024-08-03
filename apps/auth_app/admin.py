from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from import_export.admin import ImportExportModelAdmin
from django.contrib.auth.models import Group

from apps.auth_app.models import CustomUser


class NewUser(ImportExportModelAdmin, UserAdmin):
    model = CustomUser
    list_display = ['email', 'is_active', 'is_staff', 'id']
    search_fields = ['email', 'groups',]
    ordering = ['email']
    fieldsets = (
        (None, {'fields': ('first_name', 'last_name', 'email', 'password')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser',
                                    'groups')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('Personal Information',
         {'fields': ('date_of_birth', 'photo', 'about')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )


class UserLastLoginAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ['user', 'login_time', 'id']
    search_fields = ['user__email']


admin.site.register(CustomUser, NewUser)
# admin.site.register(UserLastLogin, UserLastLoginAdmin)
admin.site.unregister(Group)
