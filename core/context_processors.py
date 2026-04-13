from .cart import Cart
from .models import SiteSettings


def site_settings(request):
    return {'site_settings': SiteSettings.load()}


def cart_count(request):
    return {'cart_count': Cart(request).count}
