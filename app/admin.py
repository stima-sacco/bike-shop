from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import Bike, BikePart, CustomUser, Order, OrderItem


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


class CatalogProductAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "is_active", "updated_at")
    list_filter = ("is_active",)
    search_fields = ("slug", "name", "description")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Bike)
class BikeAdmin(CatalogProductAdmin):
    list_display = ("name", "bike_type", "price", "is_active", "updated_at")
    list_filter = ("bike_type", "is_active")
    fieldsets = (
        (None, {"fields": ("name", "slug", "bike_type", "description", "details")}),
        ("Pricing and display", {"fields": ("price", "rating", "tag", "image_url", "image_class", "specifications")}),
        ("Availability", {"fields": ("is_active",)}),
    )


@admin.register(BikePart)
class BikePartAdmin(CatalogProductAdmin):
    list_display = ("name", "part_type", "price", "is_active", "updated_at")
    list_filter = ("part_type", "is_active")
    fieldsets = (
        (None, {"fields": ("name", "slug", "part_type", "compatibility", "description", "details")}),
        ("Pricing and display", {"fields": ("price", "rating", "tag", "image_url", "image_class", "specifications")}),
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


admin.site.site_header = "Velo"
admin.site.site_title = "Velo"
admin.site.index_title = "Store management"
