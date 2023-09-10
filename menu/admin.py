from django.contrib import admin
from .models import Category, FoodItem

# Register your models here.


class CategoryAdmin(admin.ModelAdmin):
    list_display = ("category_name", "vendor", "created_at", "updated_at")
    list_display_links = ("category_name",)
    search_fields = ("category_name", "vendor__vendor_name")
    prepopulated_fields = {"slug": ("category_name",)}


class FoodItemAdmin(admin.ModelAdmin):
    list_display = ("food_title", "vendor", "category_name", "price", "is_available")
    list_display_links = ("food_title",)
    search_fields = (
        "food_title",
        "price",
        "vendor__vendor_name",
        "category_name__category_name",
    )
    prepopulated_fields = {"slug": ("food_title",)}
    list_filter = ("is_available",)


admin.site.register(Category, CategoryAdmin)
admin.site.register(FoodItem, FoodItemAdmin)
