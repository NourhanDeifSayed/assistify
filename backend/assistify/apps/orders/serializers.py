from datetime import timedelta
from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from rest_framework import serializers
from .models import Order, OrderItem, Review, TrackingUpdate

class TrackingUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrackingUpdate
        fields = (
            "date",
            "status",
            "location",
        )

class OrderItemSerializer(serializers.ModelSerializer):
    line_total = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        read_only=True,
    )

    class Meta:
        model = OrderItem
        fields = (
            "id",
            "product",
            "product_name",
            "product_emoji",
            "unit_price",
            "quantity",
            "line_total",
        )

class OrderItemInputSerializer(serializers.Serializer):
    product_id = serializers.IntegerField(
        min_value=1,
    )
    quantity = serializers.IntegerField(
        min_value=1,
        default=1,
    )

class PlaceOrderSerializer(serializers.Serializer):
    customer_email = serializers.EmailField()
    payment_method = serializers.ChoiceField(
        choices=Order.PaymentMethod.choices,
        default=Order.PaymentMethod.COD,
    )
    delivery_address = serializers.CharField(
        required=True,
        allow_blank=False,
    )
    phone = serializers.CharField(
        required=True,
        allow_blank=False,
        max_length=20,
    )
    items = OrderItemInputSerializer(
        many=True,
        min_length=1,
    )

    def validate_customer_email(self, value):
        return value.strip().lower()

    def validate_delivery_address(self, value):
        cleaned_value = value.strip()
        if len(cleaned_value) < 5:
            raise serializers.ValidationError(
                "Delivery address is too short."
            )
        return cleaned_value

    def validate_phone(self, value):
        cleaned_value = value.strip()
        normalized_phone = (
            cleaned_value
            .replace("+", "")
            .replace(" ", "")
            .replace("-", "")
            .replace("(", "")
            .replace(")", "")
        )
        if not normalized_phone.isdigit():
            raise serializers.ValidationError(
                "Phone number must contain digits only."
            )
        if len(normalized_phone) < 8:
            raise serializers.ValidationError(
                "Phone number is too short."
            )
        if len(normalized_phone) > 15:
            raise serializers.ValidationError(
                "Phone number is too long."
            )
        return cleaned_value

    def validate_items(self, items):
        from assistify.apps.products.models import Product
        validated_items = []
        seen_product_ids = set()
        for item in items:
            product_id = item["product_id"]
            if product_id in seen_product_ids:
                raise serializers.ValidationError(
                    f"Product {product_id} was added more than once."
                )
            seen_product_ids.add(product_id)
            try:
                product = Product.objects.get(
                    id=product_id,
                    is_active=True,
                )
            except Product.DoesNotExist as exc:
                raise serializers.ValidationError(
                    f"Product {product_id} was not found or is inactive."
                ) from exc
            if product.stock < item["quantity"]:
                raise serializers.ValidationError(
                    f"Product '{product.name}' does not have enough stock (available: {product.stock})."
                )
            validated_items.append(
                {
                    "product": product,
                    "quantity": item["quantity"],
                }
            )
        return validated_items

    @transaction.atomic
    def create(self, validated_data):
        items_data = validated_data.pop("items")
        subtotal = sum(
            (
                item["product"].price * item["quantity"]
                for item in items_data
            ),
            Decimal("0.00"),
        )
        shipping_fee = Decimal("50.00")
        total = subtotal + shipping_fee
        order = Order.objects.create(
            subtotal=subtotal,
            shipping_fee=shipping_fee,
            total=total,
            estimated_delivery=(
                timezone.now().date()
                + timedelta(days=7)
            ),
            **validated_data,
        )
        order_items = []
        for item in items_data:
            product = item["product"]
            product.stock -= item["quantity"]
            product.save(update_fields=["stock"])
            order_items.append(
                OrderItem(
                    order=order,
                    product=product,
                    product_name=product.name,
                    product_emoji=product.emoji,
                    unit_price=product.price,
                    quantity=item["quantity"],
                )
            )
        OrderItem.objects.bulk_create(order_items)
        TrackingUpdate.objects.create(
            order=order,
            date=timezone.now().date(),
            status="Order Placed",
            location="Warehouse",
        )
        return order

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(
        many=True,
        read_only=True,
    )
    tracking_updates = TrackingUpdateSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = Order
        fields = (
            "id",
            "order_number",
            "customer_email",
            "status",
            "payment_method",
            "subtotal",
            "shipping_fee",
            "total",
            "delivery_address",
            "phone",
            "tracking_number",
            "estimated_delivery",
            "items",
            "tracking_updates",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields

class OrderTrackingSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(
        many=True,
        read_only=True,
    )
    tracking_updates = TrackingUpdateSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = Order
        fields = (
            "order_number",
            "status",
            "tracking_number",
            "estimated_delivery",
            "items",
            "tracking_updates",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields

class GuestOrderTrackingInputSerializer(serializers.Serializer):
    order_number = serializers.CharField(
        max_length=50,
        trim_whitespace=True,
    )
    tracking_token = serializers.CharField(
        trim_whitespace=True,
    )

class OrderStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(
        choices=Order.Status.choices,
    )
    location = serializers.CharField(
        max_length=255,
        allow_blank=False,
        trim_whitespace=True,
    )
    tracking_number = serializers.CharField(
        max_length=50,
        required=False,
        allow_blank=True,
        trim_whitespace=True,
    )

    VALID_TRANSITIONS = {
        Order.Status.PLACED: {
            Order.Status.PROCESSING,
            Order.Status.CANCELLED,
        },
        Order.Status.PROCESSING: {
            Order.Status.SHIPPED,
            Order.Status.CANCELLED,
        },
        Order.Status.SHIPPED: {
            Order.Status.IN_TRANSIT,
            Order.Status.CANCELLED,
        },
        Order.Status.IN_TRANSIT: {
            Order.Status.DELIVERED,
            Order.Status.CANCELLED,
        },
        Order.Status.DELIVERED: set(),
        Order.Status.CANCELLED: set(),
    }

    def validate_location(self, value):
        cleaned_value = value.strip()
        if len(cleaned_value) < 2:
            raise serializers.ValidationError(
                "Location is too short."
            )
        return cleaned_value

    def validate(self, attrs):
        order = self.context.get("order")
        if order is None:
            raise serializers.ValidationError(
                "Order context is required."
            )
        current_status = order.status
        new_status = attrs["status"]
        if current_status == new_status:
            raise serializers.ValidationError(
                {
                    "status": (
                        "The order already has this status."
                    )
                }
            )
        allowed_statuses = self.VALID_TRANSITIONS.get(
            current_status,
            set(),
        )
        if new_status not in allowed_statuses:
            current_label = order.get_status_display()
            try:
                new_label = Order.Status(new_status).label
            except ValueError:
                new_label = new_status
            raise serializers.ValidationError(
                {
                    "status": (
                        f"Cannot change order status from "
                        f"'{current_label}' to '{new_label}'."
                    )
                }
            )
        supplied_tracking_number = attrs.get(
            "tracking_number",
            "",
        ).strip()
        if (
            new_status == Order.Status.SHIPPED
            and not supplied_tracking_number
            and not order.tracking_number
        ):
            raise serializers.ValidationError(
                {
                    "tracking_number": (
                        "Tracking number is required when "
                        "the order is shipped."
                    )
                }
            )
        attrs["tracking_number"] = supplied_tracking_number
        return attrs

class ReviewSerializer(serializers.ModelSerializer):
    order_number = serializers.CharField(
        source="order.order_number",
        read_only=True,
    )
    user_email = serializers.EmailField(
        source="user.email",
        read_only=True,
    )
    products = serializers.SerializerMethodField(
        read_only=True,
    )

    class Meta:
        model = Review
        fields = (
            "id",
            "order",
            "order_number",
            "user_email",
            "products",
            "rating",
            "comment",
            "created_at",
        )
        read_only_fields = (
            "id",
            "order_number",
            "user_email",
            "products",
            "created_at",
        )

    def get_products(self, obj):
        return [
            {
                "product_id": item.product_id,
                "product_name": item.product_name,
                "product_emoji": item.product_emoji,
            }
            for item in obj.order.items.all()
        ]

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError(
                "Rating must be between 1 and 5."
            )
        return value

    def validate_comment(self, value):
        cleaned_value = value.strip()
        if len(cleaned_value) > 2000:
            raise serializers.ValidationError(
                "Comment must not exceed 2000 characters."
            )
        return cleaned_value

    def validate_order(self, order):
        request = self.context.get("request")
        if request is None or not request.user.is_authenticated:
            raise serializers.ValidationError(
                "Authentication is required."
            )
        if order.user_id != request.user.id:
            raise serializers.ValidationError(
                "You cannot review this order."
            )
        if order.status != Order.Status.DELIVERED:
            raise serializers.ValidationError(
                "The order can only be reviewed after delivery."
            )
        if Review.objects.filter(order=order).exists():
            raise serializers.ValidationError(
                "This order has already been reviewed."
            )
        return order