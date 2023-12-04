from vendor.models import Vendor
from django.conf import settings


def get_vendor(request):
    try:
        vendor = Vendor.objects.get(user=request.user)
    except:
        vendor = None
    return dict(vendor=vendor)


def get_mapbox_api(request):
    return {"MAPBOX_API_KEY": settings.MAPBOX_API_KEY}
