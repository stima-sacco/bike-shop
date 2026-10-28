from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme

from .cart import CART_SESSION_KEY, format_kes, get_cart, get_cart_items, get_cart_total
from .catalog import product_gallery, product_to_dict
from .forms import CheckoutForm, CustomUserCreationForm, SignInForm
from .models import Bike, BikePart, Order, OrderItem


def index(request):
    products = [
        {**product_to_dict(product), "price_label": format_kes(product.price)}
        for product in Bike.objects.filter(is_active=True)
    ]
    spares = [
        {**product_to_dict(product), "price_label": format_kes(product.price)}
        for product in BikePart.objects.filter(is_active=True)
    ]
    return render(request, "app/index.html", {"products": products, "spares": spares})


def product_detail(request, product_id):
    product = Bike.objects.filter(pk=product_id, is_active=True).first()
    if product is None:
        product = BikePart.objects.filter(pk=product_id, is_active=True).first()
    if product is None:
        raise Http404("Product not found.")
    return render(
        request,
        "app/product_detail.html",
        {
            "product": {
                **product_to_dict(product),
                "price_label": format_kes(product.price),
                "gallery": product_gallery(product),
            },
        },
    )


def add_to_cart(request, product_id):
    if request.method != "POST":
        return redirect("app:index")
    product = Bike.objects.filter(pk=product_id, is_active=True).first()
    if product is None:
        product = BikePart.objects.filter(pk=product_id, is_active=True).first()
    if product is None:
        messages.error(request, "That product is not available.")
        return redirect("app:index")

    cart = get_cart(request)
    cart[product_id] = min(cart.get(product_id, 0) + 1, 99)
    request.session[CART_SESSION_KEY] = cart
    messages.success(request, f"{product.name} added to your bag.")
    return redirect("app:cart")


def cart(request):
    items = get_cart_items(request)
    total = get_cart_total(items)
    return render(
        request,
        "app/cart.html",
        {
            "items": items,
            "total": total,
            "total_label": format_kes(total),
        },
    )


def update_cart(request, product_id):
    if request.method != "POST":
        return redirect("app:cart")
    cart_items = get_cart(request)
    if product_id not in cart_items:
        messages.error(request, "That product is not in your bag.")
        return redirect("app:cart")
    product = Bike.objects.filter(pk=product_id).first()
    if product is None:
        product = BikePart.objects.filter(pk=product_id).first()
    if product is None:
        messages.error(request, "That product is not in your bag.")
        return redirect("app:cart")

    try:
        quantity = int(request.POST.get("quantity", ""))
    except ValueError:
        messages.error(request, "Enter a valid quantity.")
        return redirect("app:cart")

    if quantity <= 0:
        cart_items.pop(product_id)
        messages.info(request, f"{product.name} removed from your bag.")
    elif quantity > 99:
        messages.error(request, "The maximum quantity per bike is 99.")
        return redirect("app:cart")
    else:
        cart_items[product_id] = quantity
        messages.success(request, "Your bag has been updated.")

    request.session[CART_SESSION_KEY] = cart_items
    return redirect("app:cart")


def remove_from_cart(request, product_id):
    if request.method != "POST":
        return redirect("app:cart")
    cart_items = get_cart(request)
    if product_id in cart_items:
        cart_items.pop(product_id)
        request.session[CART_SESSION_KEY] = cart_items
        product = Bike.objects.filter(pk=product_id).first()
        if product is None:
            product = BikePart.objects.filter(pk=product_id).first()
        if product is not None:
            messages.info(request, f"{product.name} removed from your bag.")
    return redirect("app:cart")


def register(request):
    if request.user.is_authenticated:
        return redirect("app:cart")
    form = CustomUserCreationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, "Your account is ready. You can now check out.")
        next_url = request.POST.get("next", "")
        if next_url and url_has_allowed_host_and_scheme(
            next_url,
            allowed_hosts={request.get_host()},
            require_https=request.is_secure(),
        ):
            return redirect(next_url)
        return redirect("app:cart")
    return render(
        request,
        "app/register.html",
        {"form": form, "next": request.POST.get("next") or request.GET.get("next", "")},
    )


def sign_in(request):
    if request.user.is_authenticated:
        return redirect("app:cart")
    form = SignInForm(request, data=request.POST or None)
    next_url = request.POST.get("next") or request.GET.get("next", "")
    if request.method == "POST" and form.is_valid():
        login(request, form.get_user())
        if next_url and url_has_allowed_host_and_scheme(
            next_url,
            allowed_hosts={request.get_host()},
            require_https=request.is_secure(),
        ):
            return redirect(next_url)
        return redirect("app:cart")
    return render(request, "app/login.html", {"form": form, "next": next_url})


def sign_out(request):
    if request.method == "POST":
        logout(request)
        messages.info(request, "You have been signed out.")
    return redirect("app:index")


@login_required(login_url="app:login")
def checkout(request):
    items = get_cart_items(request)
    if not items:
        messages.info(request, "Add a bike to your bag before checking out.")
        return redirect("app:cart")

    total = get_cart_total(items)
    form = CheckoutForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        with transaction.atomic():
            order = Order.objects.create(
                user=request.user,
                phone=form.cleaned_data["phone"],
                delivery_address=form.cleaned_data["delivery_address"],
                county=form.cleaned_data["county"],
                payment_method=form.cleaned_data["payment_method"],
                total=total,
            )
            OrderItem.objects.bulk_create(
                [
                    OrderItem(
                        order=order,
                        product_name=item["name"],
                        quantity=item["quantity"],
                        unit_price=item["unit_price"],
                    )
                    for item in items
                ]
            )
        request.session.pop(CART_SESSION_KEY, None)
        return redirect("app:order_confirmation", order_number=order.order_number)

    return render(
        request,
        "app/checkout.html",
        {
            "form": form,
            "items": items,
            "total_label": format_kes(total),
        },
    )


@login_required(login_url="app:login")
def order_confirmation(request, order_number):
    order = get_object_or_404(
        Order.objects.prefetch_related("items"),
        order_number=order_number,
        user=request.user,
    )
    return render(
        request,
        "app/order_confirmation.html",
        {
            "order": order,
            "total_label": format_kes(order.total),
            "item_lines": [
                {
                    "item": item,
                    "line_total_label": format_kes(item.line_total),
                }
                for item in order.items.all()
            ],
        },
    )
