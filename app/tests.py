from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from app.models import Bike, BikePart


class StorefrontTests(TestCase):
    def test_homepage_renders_product_collection(self):
        response = self.client.get(reverse("app:index"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Find your")
        self.assertContains(response, "The Sunday")
        self.assertContains(response, "The Longway")
        self.assertContains(response, "The Anywhere")
        self.assertContains(response, "The Goodtime")
        self.assertContains(response, "Bicycle")
        self.assertContains(response, "Everyday Chain Kit")
        self.assertContains(response, "KSh 84,900")
        self.assertEqual(len(response.context["products"]), 4)
        self.assertEqual(len(response.context["spares"]), 4)

    def test_product_details_render_bikes_and_spares(self):
        bike_response = self.client.get(reverse("app:product_detail", args=["sunday"]))
        spare_response = self.client.get(reverse("app:product_detail", args=["chain-kit"]))

        self.assertEqual(bike_response.status_code, 200)
        self.assertContains(bike_response, "The Sunday")
        self.assertContains(bike_response, "Lightweight alloy frame")
        self.assertEqual(spare_response.status_code, 200)
        self.assertContains(spare_response, "Everyday Chain Kit")
        self.assertContains(spare_response, "Compatibility and exact specifications can vary")

    def test_unknown_product_details_return_404(self):
        response = self.client.get(reverse("app:product_detail", args=["unknown-product"]))

        self.assertEqual(response.status_code, 404)

    def test_bike_and_spare_parts_are_database_models(self):
        bike = Bike.objects.get(slug="sunday")
        part = BikePart.objects.get(slug="chain-kit")

        self.assertEqual(bike.bike_type, Bike.Type.CITY)
        self.assertEqual(bike.price, 84900)
        self.assertEqual(part.part_type, BikePart.Type.DRIVETRAIN)
        self.assertIn("6- and 7-speed", part.compatibility)

    def test_inactive_products_are_not_listed_or_added_to_cart(self):
        Bike.objects.filter(slug="sunday").update(is_active=False)

        response = self.client.get(reverse("app:index"))
        add_response = self.client.post(reverse("app:add_to_cart", args=["sunday"]))

        self.assertNotContains(response, "The Sunday")
        self.assertRedirects(add_response, reverse("app:index"))
        self.assertNotIn("sunday", self.client.session.get("bike_shop_cart", {}))

    def test_homepage_loads_responsive_assets(self):
        response = self.client.get(reverse("app:index"))

        self.assertContains(response, "app/css/storefront.css")
        self.assertContains(response, "app/js/storefront.js")
        self.assertContains(response, 'name="viewport"')

    def test_cart_add_update_and_remove_use_session(self):
        add_response = self.client.post(reverse("app:add_to_cart", args=["sunday"]))
        self.assertRedirects(add_response, reverse("app:cart"))
        self.assertContains(self.client.get(reverse("app:cart")), "KSh 84,900")

        update_response = self.client.post(
            reverse("app:update_cart", args=["sunday"]),
            {"quantity": "2"},
        )
        self.assertRedirects(update_response, reverse("app:cart"))
        self.assertContains(self.client.get(reverse("app:cart")), "KSh 169,800")

        remove_response = self.client.post(reverse("app:remove_from_cart", args=["sunday"]))
        self.assertRedirects(remove_response, reverse("app:cart"))
        self.assertContains(self.client.get(reverse("app:cart")), "Your bag is taking a breather")

    def test_spares_can_be_added_to_cart(self):
        response = self.client.post(reverse("app:add_to_cart", args=["chain-kit"]))

        self.assertRedirects(response, reverse("app:cart"))
        self.assertContains(self.client.get(reverse("app:cart")), "Everyday Chain Kit")
        self.assertContains(self.client.get(reverse("app:cart")), "KSh 2,500")

    def test_checkout_requires_an_account(self):
        self.client.post(reverse("app:add_to_cart", args=["sunday"]))

        response = self.client.get(reverse("app:checkout"))

        self.assertRedirects(
            response,
            f"{reverse('app:login')}?next={reverse('app:checkout')}",
        )

    def test_registration_preserves_cart_and_checkout_creates_order(self):
        self.client.post(reverse("app:add_to_cart", args=["sunday"]))
        register_response = self.client.post(
            reverse("app:register"),
            {
                "name": "Rider One",
                "email": "rider@example.com",
                "password1": "SafeRidePassword!743",
                "password2": "SafeRidePassword!743",
                "next": reverse("app:checkout"),
            },
        )
        self.assertRedirects(register_response, reverse("app:checkout"))
        self.assertTrue(get_user_model().objects.filter(email="rider@example.com").exists())

        response = self.client.post(
            reverse("app:checkout"),
            {
                "phone": "0712 345 678",
                "delivery_address": "12 Riverside Drive",
                "county": "Nairobi",
                "payment_method": "mpesa",
            },
        )

        order = get_user_model().objects.get(email="rider@example.com").orders.get()
        self.assertRedirects(
            response,
            reverse("app:order_confirmation", args=[order.order_number]),
        )
        self.assertEqual(str(order.total), "84900.00")
        self.assertEqual(order.phone, "+254712345678")
        self.assertEqual(order.items.get().product_name, "The Sunday")
        self.assertEqual(order.payment_status, "pending")
        self.assertEqual(self.client.session.get("bike_shop_cart"), None)

    def test_invalid_kenyan_phone_keeps_checkout_open(self):
        user = get_user_model().objects.create_user(
            email="rider@example.com",
            password="SafeRidePassword!743",
            name="Rider One",
        )
        self.client.force_login(user)
        self.client.post(reverse("app:add_to_cart", args=["sunday"]))

        response = self.client.post(
            reverse("app:checkout"),
            {
                "phone": "123",
                "delivery_address": "12 Riverside Drive",
                "county": "Nairobi",
                "payment_method": "mpesa",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Enter a valid Kenyan mobile number")
        self.assertEqual(user.orders.count(), 0)
