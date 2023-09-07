from django.contrib import admin

# Register your models here.

from vendor.models import Vendor


class AdminVendor(admin.ModelAdmin):
    list_display = ("user", "vendor_name", "is_approved", "created_at")
    list_display_links = ("user", "vendor_name")
    list_editable = ("is_approved",)


admin.site.register(Vendor, AdminVendor)
