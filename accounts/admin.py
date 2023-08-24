from django.contrib import admin
from .models import User, UserProfile
from django.contrib.auth.admin import (
    UserAdmin,
)  # Protect to edit password via admin panel

# Register your models here.


class CustomUserAdmin(UserAdmin, admin.ModelAdmin):
    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()
    list_display = (
        "username",
        "first_name",
        "last_name",
        "email",
        "is_admin",
        "role",
        "is_active",
        "date_joined",
    )
    ordering = ("-date_joined",)


admin.site.register(User, CustomUserAdmin)
admin.site.register(UserProfile)
