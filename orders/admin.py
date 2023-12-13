from django.contrib import admin
from .models import Order, Payment, OrderedFood


# Register your models here.


class PaymentAdmin(admin.ModelAdmin):
    list_display = ("user", "transaction_id", "amount", "status", "created_at")
    list_display_links = ("user",)


class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "payment_id",
        "order_number",
        "user",
        "pin_code",
        "total",
        "is_ordered",
        "status",
    )
    list_display_links = ("user", "payment_id")


class OrderFoodAdmin(admin.ModelAdmin):
    list_display = (
        "order",
        "payment",
        "user",
        "quantity",
        "price",
        "amount",
        "updated_at",
    )
    list_display_links = ("order", "payment", "user")


admin.site.register(Payment, PaymentAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderedFood, OrderFoodAdmin)
