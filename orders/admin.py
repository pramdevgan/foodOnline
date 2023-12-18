from django.contrib import admin
from .models import Order, Payment, OrderedFood


# Register your models here.


class OrderedFoodInline(admin.TabularInline):
    model = OrderedFood
    readonly_fields = (
        "order",
        "payment",
        "user",
        "fooditem",
        "quantity",
        "price",
        "amount",
    )
    extra = 0


class PaymentAdmin(admin.ModelAdmin):
    list_display = ("user", "transaction_id", "amount", "status", "created_at")
    list_display_links = ("user",)


class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "payment_id",
        "order_number",
        "user",
        "pin_code",
        "total",
        "is_ordered",
        "status",
    )
    inlines = [OrderedFoodInline]
    list_display_links = ("order_number",)


class OrderFoodAdmin(admin.ModelAdmin):
    list_display = (
        "fooditem",
        "order",
        "payment",
        "user",
        "quantity",
        "price",
        "amount",
        "updated_at",
    )
    list_display_links = (
        "fooditem",
        "order",
    )


admin.site.register(Payment, PaymentAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderedFood, OrderFoodAdmin)
