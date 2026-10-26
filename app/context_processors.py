from .cart import get_cart_count


def storefront(request):
    return {"cart_count": get_cart_count(request)}
