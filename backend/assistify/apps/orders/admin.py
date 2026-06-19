from django.contrib import admin
from .models import Order, OrderItem, TrackingUpdate, Review

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("line_total",)

class TrackingInline(admin.TabularInline):
    model = TrackingUpdate
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "order_number",
        "customer_name",
        "customer_email",
        "phone",
        "delivery_address",
        "get_items_summary",
        "get_items_quantity",
        "total",
        "payment_method",
        "status",
        "created_at",
    )
    list_filter = ("status", "payment_method", "created_at")
    search_fields = (
        "order_number",
        "customer_name",
        "customer_email",
        "phone",
        "delivery_address",
    )
    inlines = [OrderItemInline, TrackingInline]
    readonly_fields = ("order_number", "created_at", "updated_at")

    def get_items_summary(self, obj):
        return ", ".join([f"{item.product_name}" for item in obj.items.all()])
    get_items_summary.short_description = "Product/items"

    def get_items_quantity(self, obj):
        return sum(item.quantity for item in obj.items.all())
    get_items_quantity.short_description = "Quantity"

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("order", "product_name", "unit_price", "quantity", "line_total")
    search_fields = ("order__order_number", "product_name")

@admin.register(TrackingUpdate)
class TrackingUpdateAdmin(admin.ModelAdmin):
    list_display = ("order", "date", "status", "location")
    list_filter = ("date", "status")
    search_fields = ("order__order_number", "status", "location")

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("order", "rating", "created_at")
    list_filter = ("rating",)