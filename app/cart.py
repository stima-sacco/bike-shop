from decimal import Decimal

from .catalog import product_to_dict
from .models import Bike, BikePart

CART_SESSION_KEY = "bike_shop_cart"

def get_cart(request):
    stored_cart = request.session.get(CART_SESSION_KEY, {})
    if not isinstance(stored_cart, dict):
        request.session[CART_SESSION_KEY] = {}
        return {}

    stored_ids = [
        product_id
        for product_id in stored_cart
        if isinstance(product_id, str)
    ]
    valid_ids = set(
        Bike.objects.filter(slug__in=stored_ids, is_active=True).values_list("slug", flat=True)
    )
    valid_ids.update(
        BikePart.objects.filter(slug__in=stored_ids, is_active=True).values_list("slug", flat=True)
    )

    cart = {}
    for product_id, quantity in stored_cart.items():
        if product_id not in valid_ids or not isinstance(quantity, int) or isinstance(quantity, bool):
            continue
        if 1 <= quantity <= 99:
            cart[product_id] = quantity

    if cart != stored_cart:
        request.session[CART_SESSION_KEY] = cart
    return cart


def get_cart_items(request):
    cart = get_cart(request)
    if not cart:
        return []
    products = {
        product.slug: product
        for product in Bike.objects.filter(slug__in=cart)
    }
    products.update(
        {
            product.slug: product
            for product in BikePart.objects.filter(slug__in=cart)
        }
    )
    items = []
    for product_id, quantity in cart.items():
        product = products.get(product_id)
        if product is None or not product.is_active:
            continue
        product_data = product_to_dict(product)
        unit_price = Decimal(product.price)
        items.append(
            {
                **product_data,
                "quantity": quantity,
                "unit_price": unit_price,
                "line_total": unit_price * quantity,
                "price_label": format_kes(unit_price),
                "line_total_label": format_kes(unit_price * quantity),
            }
        )
    return items


def get_cart_total(items):
    return sum((item["line_total"] for item in items), Decimal("0.00"))


def format_kes(amount):
    return f"KSh {amount:,.0f}"


def get_cart_count(request):
    return sum(get_cart(request).values())
