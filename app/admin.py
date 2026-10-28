from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.db import models
from django.utils.html import format_html

from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import Bike, BikeImage, BikePart, BikePartImage, CustomUser, Order, OrderItem
from .widgets import CameraImageWidget


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ('email', 'is_staff', 'is_active',)
    list_filter = ('email', 'is_staff', 'is_active',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Permissions', {'fields': ('is_staff', 'is_active')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )
    search_fields = ('email',)
    ordering = ('email',)


admin.site.register(CustomUser, CustomUserAdmin)


class ProductImageInline(admin.StackedInline):
    extra = 1
    fields = (("image", "image_preview"), ("caption", "sort_order"))
    readonly_fields = ("image_preview",)
    formfield_overrides = {models.ImageField: {"widget": CameraImageWidget}}
    verbose_name = "Additional image"
    verbose_name_plural = "Additional images"

    @admin.display(description="Preview")
    def image_preview(self, obj):
        if not obj or not obj.image:
            return "—"
        return format_html('<img src="{}" alt="" style="max-height:120px;border-radius:4px">', obj.image.url)


class BikeImageInline(ProductImageInline):
    model = BikeImage


class BikePartImageInline(ProductImageInline):
    model = BikePartImage


class CatalogProductAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "is_active", "updated_at")
    list_filter = ("is_active",)
    search_fields = ("slug", "name", "description")
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("image_preview",)
    formfield_overrides = {models.ImageField: {"widget": CameraImageWidget}}

    @admin.display(description="Preview")
    def image_preview(self, obj):
        src = obj.display_image if obj else ""
        if not src:
            return "—"
        return format_html('<img src="{}" alt="" style="max-height:160px;border-radius:4px">', src)


@admin.register(Bike)
class BikeAdmin(CatalogProductAdmin):
    list_display = ("name", "bike_type", "price", "is_active", "updated_at")
    list_filter = ("bike_type", "is_active")
    inlines = (BikeImageInline,)
    fieldsets = (
        (None, {"fields": ("name", "slug", "bike_type", "description", "details")}),
        ("Image", {"fields": ("image", "image_preview", "image_url", "image_class"), "description": "Upload a photo or take one with the camera. Uploaded images take priority over the image URL."}),
        ("Pricing and display", {"fields": ("price", "rating", "tag", "specifications")}),
        ("Availability", {"fields": ("is_active",)}),
    )


@admin.register(BikePart)
class BikePartAdmin(CatalogProductAdmin):
    list_display = ("name", "part_type", "price", "is_active", "updated_at")
    list_filter = ("part_type", "is_active")
    inlines = (BikePartImageInline,)
    fieldsets = (
        (None, {"fields": ("name", "slug", "part_type", "compatibility", "description", "details")}),
        ("Image", {"fields": ("image", "image_preview", "image_url", "image_class"), "description": "Upload a photo or take one with the camera. Uploaded images take priority over the image URL."}),
        ("Pricing and display", {"fields": ("price", "rating", "tag", "specifications")}),
        ("Availability", {"fields": ("is_active",)}),
    )


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product_name", "quantity", "unit_price")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("order_number", "user", "status", "payment_status", "payment_method", "total", "created_at")
    list_filter = ("status", "payment_status", "payment_method", "created_at")
    search_fields = ("order_number", "user__email", "phone")
    readonly_fields = ("order_number", "user", "phone", "delivery_address", "county", "payment_method", "total", "created_at")
    inlines = (OrderItemInline,)


admin.site.site_header = "Bike Shop"
admin.site.site_title = "Bike Shop"
admin.site.index_title = "Store management"
