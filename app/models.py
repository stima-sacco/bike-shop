from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.conf import settings
import uuid

from .managers import CustomUserManager


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_('email address'), unique=True)
    name = models.CharField(max_length=255, default="")
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email


class CatalogProduct(models.Model):
    slug = models.SlugField(max_length=80, primary_key=True)
    name = models.CharField(max_length=120)
    description = models.CharField(max_length=200)
    details = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    specifications = models.JSONField(default=list, blank=True)
    image_url = models.URLField(max_length=500, blank=True)
    image_class = models.CharField(max_length=60, blank=True)
    tag = models.CharField(max_length=60, blank=True)
    rating = models.DecimalField(max_digits=2, decimal_places=1, default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ("name",)

    @property
    def id(self):
        return self.slug

    def __str__(self):
        return self.name


class Bike(CatalogProduct):
    class Type(models.TextChoices):
        CITY = "city", "City"
        ROAD = "road", "Road"
        ELECTRIC = "electric", "Electric"

    bike_type = models.CharField(max_length=20, choices=Type.choices)

    @property
    def category(self):
        return self.bike_type

    @property
    def type(self):
        return dict(self.Type.choices)[self.bike_type]


class BikePart(CatalogProduct):
    class Type(models.TextChoices):
        DRIVETRAIN = "drivetrain", "Drivetrain"
        BRAKES = "brakes", "Brakes"
        TYRES = "tyres", "Tyres & tubes"
        SAFETY = "safety", "Safety"
        OTHER = "other", "Other"

    part_type = models.CharField(max_length=20, choices=Type.choices, default=Type.OTHER)
    compatibility = models.CharField(max_length=255, blank=True)

    @property
    def category(self):
        return "spares"

    @property
    def type(self):
        return f"Spare / {dict(self.Type.choices)[self.part_type]}"


class Order(models.Model):
    class PaymentMethod(models.TextChoices):
        MPESA = "mpesa", "M-Pesa"
        CASH_ON_DELIVERY = "cash_on_delivery", "Cash on delivery"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending confirmation"
        CONFIRMED = "confirmed", "Confirmed"
        FULFILLED = "fulfilled", "Fulfilled"
        CANCELLED = "cancelled", "Cancelled"

    class PaymentStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        PAID = "paid", "Paid"
        FAILED = "failed", "Failed"
        REFUNDED = "refunded", "Refunded"

    order_number = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="orders")
    phone = models.CharField(max_length=16)
    delivery_address = models.CharField(max_length=255)
    county = models.CharField(max_length=100)
    payment_method = models.CharField(max_length=20, choices=PaymentMethod.choices)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    payment_status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING,
    )
    total = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Order {self.order_number}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product_name = models.CharField(max_length=120)
    quantity = models.PositiveSmallIntegerField()
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)

    @property
    def line_total(self):
        return self.unit_price * self.quantity

    def __str__(self):
        return f"{self.quantity} x {self.product_name}"