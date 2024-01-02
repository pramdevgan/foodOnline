import json

from django.db import models

from accounts.models import User
from menu.models import FoodItem
from vendor.models import Vendor


# Create your models here.

request_object = ""


class Payment(models.Model):
    PAYMENT_METHOD = (
        ("PayPal", "PayPal"),
        ("RazorPay", "RazorPay"),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    transaction_id = models.CharField(max_length=100)
    payment_method = models.CharField(max_length=100, choices=PAYMENT_METHOD)
    amount = models.CharField(max_length=10)
    status = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.transaction_id


class Order(models.Model):
    STATUS = (
        ("New", "New"),
        ("Accepted", "Accepted"),
        ("Completed", "Completed"),
        ("Cancelled", "Cancelled"),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    payment = models.ForeignKey(
        Payment, on_delete=models.SET_NULL, blank=True, null=True
    )
    vendors = models.ManyToManyField(Vendor, blank=True)
    order_number = models.CharField(max_length=20)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    email = models.EmailField()
    address = models.CharField(max_length=200)
    country = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    pin_code = models.CharField(max_length=10)
    total = models.FloatField()
    tax_data = models.JSONField(
        blank=True,
        help_text="Data format:{'tax_type': {'tax_percentage': 'tax_amount'}}",
        null=True,
    )
    total_data = models.JSONField(blank=True, null=True)
    total_tax = models.FloatField()
    payment_method = models.CharField(max_length=25)
    status = models.CharField(max_length=20, choices=STATUS, default="New")
    is_ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Concatenate first_name and last_name
    @property
    def name(self):
        return f"{self.first_name} {self.last_name}"

    def order_placed_to(self):
        return ", ".join([str(i) for i in self.vendors.all()])

    def get_total_by_vendor(self):
        vendor = Vendor.objects.get(user=request_object.user)
        if self.total_data:
            total_data = json.loads(self.total_data)
            data = total_data.get(str(vendor.id))

            if data:
                subtotal = 0
                tax = 0
                tax_dict = {}

                for key, val in data.items():
                    subtotal += float(key)
                    val = val.replace("'", '"')
                    val = json.loads(val)
                    tax_dict.update(val)

                    # calculate tax
                    for i in val:
                        for j in val[i]:
                            tax += float(val[i][j])
                grand_total = float(subtotal) + float(tax)
                context = {
                    "subtotal": subtotal,
                    "tax_dict": tax_dict,
                    "grand_total": grand_total,
                }
                return context
        return {"grand_total": 0, "subtotal": 0, "tax_dict": 0}

    def __str__(self):
        return self.order_number


class OrderedFood(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    payment = models.ForeignKey(
        Payment, on_delete=models.SET_NULL, blank=True, null=True
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    fooditem = models.ForeignKey(FoodItem, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.FloatField()
    amount = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.fooditem.food_title}"
