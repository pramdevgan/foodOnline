import simplejson as json
from django.http import HttpResponse, JsonResponse

from django.shortcuts import render, redirect

from marketplace.models import Cart
from marketplace.context_processors import get_cart_amounts
from orders.forms import OrderForm
from .models import Order, Payment, OrderedFood
from .utils import generate_order_number
from accounts.utils import send_notification
from django.contrib.auth.decorators import login_required
import razorpay
from foodOnline.settings import RZP_KEY_ID, RZP_KEY_SECRET

# Create your views here.
client = razorpay.Client(auth=(RZP_KEY_ID, RZP_KEY_SECRET))


@login_required(login_url="login")
def place_order(request):
    cart_items = Cart.objects.filter(user=request.user).order_by("created_at")
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect("marketplace")

    subtotal = get_cart_amounts(request)["subtotal"]
    total_tax = get_cart_amounts(request)["tax"]
    grand_total = get_cart_amounts(request)["grand_total"]
    tax_data = get_cart_amounts(request)["tax_dict"]

    if request.method == "POST":
        form = OrderForm(request.POST)
        if form.is_valid():
            order = Order()
            order.first_name = form.cleaned_data["first_name"]
            order.last_name = form.cleaned_data["last_name"]
            order.phone_number = form.cleaned_data["phone_number"]
            order.email = form.cleaned_data["email"]
            order.address = form.cleaned_data["address"]
            order.country = form.cleaned_data["country"]
            order.state = form.cleaned_data["state"]
            order.city = form.cleaned_data["city"]
            order.pin_code = form.cleaned_data["pin_code"]
            order.user = request.user
            order.total = grand_total
            order.tax_data = json.dumps(tax_data)
            order.total_tax = total_tax
            order.payment_method = request.POST["payment_method"]
            order.save()
            order.order_number = generate_order_number(order.id)
            order.save()

            # RazorPay Payment
            DATA = {
                "amount": float(order.total) * 100,
                "currency": "INR",
                "receipt": "receipt#" + order.order_number,
                "notes": {"key1": "value3", "key2": "value2"},
            }
            rzp_order = client.order.create(data=DATA)
            rzp_order_id = rzp_order["id"]
            context = {
                "order": order,
                "cart_items": cart_items,
                "rzp_order_id": rzp_order_id,
                "RZP_KEY_ID": RZP_KEY_ID,
                "rzp_amount": float(order.total) * 100,
            }
            return render(request, "orders/place_order.html", context)

        else:
            print(form.errors)
    context = {}
    return render(request, "orders/place_order.html", context)


@login_required(login_url="login")
def payments(request):
    # Check if the req is ajax or not
    if (
        request.headers.get("x-requested-with") == "XMLHttpRequest"
        and request.method == "POST"
    ):
        # Store the payment details in the payment model
        order_number = request.POST.get("order_number")
        transaction_id = request.POST.get("transaction_id")
        payment_method = request.POST.get("payment_method")
        status = request.POST.get("status")

        order = Order.objects.get(user=request.user, order_number=order_number)
        payment = Payment(
            user=request.user,
            transaction_id=transaction_id,
            payment_method=payment_method,
            amount=order.total,
            status=status,
        )
        payment.save()
        # Update the order model
        order.payment = payment
        order.is_ordered = True
        order.save()

        # Move the cart items to ordered food model
        cart_items = Cart.objects.filter(
            user=request.user,
        )
        for item in cart_items:
            ordered_food = OrderedFood()
            ordered_food.order = order
            ordered_food.payment = payment
            ordered_food.user = request.user
            ordered_food.fooditem = item.fooditem
            ordered_food.quantity = item.quantity
            ordered_food.price = item.fooditem.price
            ordered_food.amount = item.fooditem.price * item.quantity  # Ttl amount
            ordered_food.save()
        # send order confirmation email to the customer
        mail_subject = "Thank you for Ordering with us."
        mail_template = "orders/order_confirmation.html"
        context = {"user": request.user, "order": order, "to_email": order.email}
        send_notification(mail_subject, mail_template, context)

        # Send order received email to the vendor
        mail_subject = "You have new order."
        mail_template = "orders/new_order_receive.html"
        to_emails = []
        for i in cart_items:
            if i.fooditem.vendor.user.email not in to_emails:
                to_emails.append(i.fooditem.vendor.user.email)
        context = {"order": order, "to_email": to_emails}
        send_notification(mail_subject, mail_template, context)

        # Clear the cart if the pyment is success
        # cart_items.delete()
        # Return back to ajax with status SUCCESS or FAILURE
        response = {
            "order_number": order_number,
            "transaction_id": transaction_id,
        }
        return JsonResponse(response)
    return HttpResponse("Payments View")


def order_complete(request):
    order_number = request.GET.get("order_number")
    transaction_id = request.GET.get("transaction_id")
    try:
        order = Order.objects.get(
            order_number=order_number,
            payment__transaction_id=transaction_id,
            is_ordered=True,
        )
        ordered_food = OrderedFood.objects.filter(order=order)
        subtotal = 0
        for item in ordered_food:
            subtotal += item.price * item.quantity
        tax_data = json.loads(order.tax_data)
        context = {
            "order": order,
            "ordered_food": ordered_food,
            "subtotal": subtotal,
            "tax_data": tax_data,
        }
        return render(request, "orders/order_complete.html", context)
    except:
        return redirect("home")