from django.contrib import admin
from .models import User, UserProfile
from django.contrib.auth.admin import (
    UserAdmin,
)  # Protect to edit password via admin panel

# Register your models here.


class AdminUser(UserAdmin, admin.ModelAdmin):
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


class AdminUserProfile(admin.ModelAdmin):
    list_display = ("user", "country", "city", "pin_code", "created_at")


admin.site.register(User, AdminUser)
admin.site.register(UserProfile, AdminUserProfile)
