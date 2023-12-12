from datetime import date, datetime
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.measure import D
from django.db.models import Prefetch, Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect

from marketplace.context_processors import get_cart_counter, get_cart_amounts
from marketplace.models import Cart
from menu.models import Category, FoodItem
from vendor.models import Vendor, OpeningHour
from django.contrib.auth.decorators import login_required
from django.contrib.gis.db.models.functions import Distance

# Create your views here.


def marketplace(request):
    vendors = Vendor.objects.filter(is_approved=True, user__is_active=True)
    vendor_count = vendors.count()
    context = {
        "vendors": vendors,
        "vendor_count": vendor_count,
    }
    return render(request, "marketplace/listing.html", context)


def vendor_detail(request, vendor_slug):
    vendor = get_object_or_404(Vendor, vendor_slug=vendor_slug)

    categories = Category.objects.filter(vendor=vendor).prefetch_related(
        Prefetch("fooditems", queryset=FoodItem.objects.filter(is_available=True))
    )

    opening_hours = OpeningHour.objects.filter(vendor=vendor).order_by(
        "day", "-from_hour"
    )

    # Check Current day's opening hours.
    today_date = date.today()
    today = today_date.isoweekday()
    current_opening_hours = OpeningHour.objects.filter(vendor=vendor, day=today)

    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
    else:
        cart_items = None
    context = {
        "vendor": vendor,
        "categories": categories,
        "cart_items": cart_items,
        "opening_hours": opening_hours,
        "current_opening_hours": current_opening_hours,
    }
    return render(request, "marketplace/vendor_detail.html", context)


def add_to_cart(request, food_id=None):
    if request.user.is_authenticated:
        if request.is_ajax():
            # Check if the food item exists
            try:
                fooditem = FoodItem.objects.get(id=food_id)
                # Check if the user has already added that food to the cart
                try:
                    chkCart = Cart.objects.get(user=request.user, fooditem=fooditem)
                    # Increase the cart qty
                    chkCart.quantity += 1
                    chkCart.save()
                    return JsonResponse(
                        {
                            "status": "Success",
                            "message": "Increased the cart qty",
                            "cart_counter": get_cart_counter(request),
                            "qty": chkCart.quantity,
                            "cart_amount": get_cart_amounts(request),
                        }
                    )
                except:
                    chkCart = Cart.objects.create(
                        user=request.user, fooditem=fooditem, quantity=1
                    )
                    return JsonResponse(
                        {
                            "status": "Success",
                            "message": "Added the food to the cart",
                            "cart_counter": get_cart_counter(request),
                            "qty": chkCart.quantity,
                            "cart_amount": get_cart_amounts(request),
                        }
                    )

            except:
                return JsonResponse(
                    {"status": "Failed", "message": "This food Does not Exist"}
                )
        else:
            return JsonResponse({"status": "Failed", "message": "Invalid Request"})

    return JsonResponse(
        {"status": "login_required", "message": "Please login to continue"}
    )


def decrease_cart(request, food_id):
    if request.user.is_authenticated:
        if request.is_ajax():
            # Check if the food item exists
            try:
                fooditem = FoodItem.objects.get(id=food_id)
                # Check if the user has already added that food to the cart
                try:
                    chkCart = Cart.objects.get(user=request.user, fooditem=fooditem)
                    if chkCart.quantity > 1:
                        # Decrease the cart qty
                        chkCart.quantity -= 1
                        chkCart.save()
                    else:
                        chkCart.delete()
                        chkCart.quantity = 0
                    return JsonResponse(
                        {
                            "status": "Success",
                            "cart_counter": get_cart_counter(request),
                            "qty": chkCart.quantity,
                            "cart_amount": get_cart_amounts(request),
                        }
                    )
                except:
                    return JsonResponse(
                        {
                            "status": "Failed",
                            "message": "You do not have this item in your cart",
                        }
                    )

            except:
                return JsonResponse(
                    {"status": "Failed", "message": "This food Does not Exist"}
                )
        else:
            return JsonResponse({"status": "Failed", "message": "Invalid Request"})

    return JsonResponse(
        {"status": "login_required", "message": "Please login to continue"}
    )


@login_required(login_url="login")
def cart(request):
    cart_items = Cart.objects.filter(user=request.user).order_by("created_at")
    context = {"cart_items": cart_items}
    return render(request, "marketplace/cart.html", context)


def delete_cart(request, cart_id):
    if request.user.is_authenticated:
        if request.is_ajax():
            try:
                # Check if the cart item exists
                cart_item = Cart.objects.get(user=request.user, id=cart_id)
                if cart_item:
                    cart_item.delete()
                    return JsonResponse(
                        {
                            "status": "Success",
                            "message": "Cart Item has been Deleted!",
                            "cart_counter": get_cart_counter(request),
                            "cart_amount": get_cart_amounts(request),
                        }
                    )
            except:
                return JsonResponse(
                    {"status": "Failed", "message": "Cart Item Does not Exist"}
                )
    else:
        return HttpResponse({"status": "Failed", "message": "Invalid Request"})


def search(request):
    if not "address" in request.GET:
        return redirect("marketplace")
    else:
        address = request.GET["address"]
        latitude = request.GET["lat"]
        longitude = request.GET["lng"]
        radius = request.GET["radius"]
        keyword = request.GET["keyword"]

        # get vendor id's that has the food item the user is looking for
        fetch_vendor_by_foodItems = FoodItem.objects.filter(
            food_title__icontains=keyword, is_available=True
        ).values_list("vendor", flat=True)

        vendors = Vendor.objects.filter(
            Q(id__in=fetch_vendor_by_foodItems)
            | Q(vendor_name__icontains=keyword, is_approved=True, user__is_active=True)
        )

        if latitude and longitude and radius:
            pnt = GEOSGeometry("POINT(%s %s)" % (longitude, latitude))
            vendors = (
                Vendor.objects.filter(
                    Q(id__in=fetch_vendor_by_foodItems)
                    | Q(
                        vendor_name__icontains=keyword,
                        is_approved=True,
                        user__is_active=True,
                    ),
                    user_profile__location__distance_lte=(pnt, D(km=radius)),
                )
                .annotate(distance=Distance("user_profile__location", pnt))
                .order_by("distance")
            )
            for v in vendors:
                v.kms = round(v.distance.km, 2)
        vendor_count = vendors.count()
        context = {
            "vendors": vendors,
            "vendor_count": vendor_count,
            "source_location": address,
        }

        return render(request, "marketplace/listing.html", context)
