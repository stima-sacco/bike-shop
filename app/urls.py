from django.urls import path
from . import views

app_name = "app"

urlpatterns = [
    path("", views.index, name="index"),
    path("products/<slug:product_id>/", views.product_detail, name="product_detail"),
    path("cart/", views.cart, name="cart"),
    path("cart/add/<slug:product_id>/", views.add_to_cart, name="add_to_cart"),
    path("cart/update/<slug:product_id>/", views.update_cart, name="update_cart"),
    path("cart/remove/<slug:product_id>/", views.remove_from_cart, name="remove_from_cart"),
    path("account/register/", views.register, name="register"),
    path("account/login/", views.sign_in, name="login"),
    path("account/logout/", views.sign_out, name="logout"),
    path("checkout/", views.checkout, name="checkout"),
    path(
        "orders/<uuid:order_number>/",
        views.order_confirmation,
        name="order_confirmation",
    ),
]
