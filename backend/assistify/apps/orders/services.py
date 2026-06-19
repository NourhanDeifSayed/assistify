from decimal import Decimal
from typing import Any, Dict, List, Optional

from django.apps import apps
from django.core import signing
from django.db import transaction
from django.utils import timezone

from assistify.apps.orders.models import (
    Order,
    OrderItem,
    TrackingUpdate,
)
from assistify.apps.orders.email_service import send_order_confirmation


ORDER_TRACKING_TOKEN_SALT = "assistify.order.tracking"
DEFAULT_SHIPPING_FEE = Decimal("50.00")


def generate_order_tracking_token(order: Order) -> str:
    """Generate a signed token for secure guest order tracking."""
    return signing.dumps(
        {
            "order_number": order.order_number,
        },
        salt=ORDER_TRACKING_TOKEN_SALT,
        compress=True,
    )


def _normalize_quantity(quantity: Any) -> int:
    try:
        normalized_quantity = int(quantity or 1)
    except (TypeError, ValueError) as exc:
        raise ValueError(
            "Quantity must be a valid integer."
        ) from exc

    if normalized_quantity < 1 or normalized_quantity > 99:
        raise ValueError(
            "Quantity must be between 1 and 99."
        )

    return normalized_quantity


def _decimal_price(value: Any) -> Decimal:
    try:
        price = Decimal(str(value))
    except Exception as exc:
        raise ValueError(
            "The selected product has an invalid price."
        ) from exc

    if price < Decimal("0.00"):
        raise ValueError(
            "The selected product price cannot be negative."
        )

    return price.quantize(Decimal("0.01"))


def get_local_catalog_products(
    limit: int = 50,
) -> List[Dict[str, Any]]:
    """
    Return active products directly from PostgreSQL.

    This is the primary Assistify catalogue and does not depend on Shopify.
    Shopify data can optionally enrich these records inside the orchestrator.
    """
    Product = apps.get_model("products", "Product")

    try:
        normalized_limit = int(limit)
    except (TypeError, ValueError):
        normalized_limit = 50

    normalized_limit = max(1, min(normalized_limit, 200))

    products = Product.objects.filter(
        is_active=True,
    ).order_by("id")[:normalized_limit]

    result: List[Dict[str, Any]] = []

    for product in products:
        result.append(
            {
                "id": product.id,
                "product_id": product.id,
                "name": product.name,
                "title": product.name,
                "description": product.description,
                "price": str(product.price),
                "currency": getattr(product, "currency", "EGP"),
                "emoji": getattr(product, "emoji", "") or "📦",
                "features": getattr(product, "features", []) or [],
                "suitable_for": (
                    getattr(product, "suitable_for", []) or []
                ),
                "use_cases": getattr(product, "use_cases", []) or [],
                "source": "local",
            }
        )

    return result


def _resolve_local_product(
    product_id: Any = None,
    product_snapshot: Optional[Dict[str, Any]] = None,
):
    """
    Resolve an active local Product from either a local ID or a product
    snapshot. Shopify IDs are ignored when they are not valid local IDs,
    then the product name is used as a safe fallback.
    """
    Product = apps.get_model("products", "Product")
    snapshot = product_snapshot or {}

    possible_ids = (
        product_id,
        snapshot.get("product_id"),
        snapshot.get("local_product_id"),
    )

    for possible_id in possible_ids:
        if possible_id in (None, ""):
            continue

        try:
            numeric_id = int(possible_id)
        except (TypeError, ValueError):
            continue

        product = Product.objects.filter(
            pk=numeric_id,
            is_active=True,
        ).first()

        if product is not None:
            return product

    product_name = (
        snapshot.get("name")
        or snapshot.get("title")
        or ""
    ).strip()

    if product_name:
        product = Product.objects.filter(
            name__iexact=product_name,
            is_active=True,
        ).first()

        if product is not None:
            return product

        product = Product.objects.filter(
            name__icontains=product_name,
            is_active=True,
        ).first()

        if product is not None:
            return product

    return None


@transaction.atomic
def create_order_from_chat(
    product_id: Any = None,
    phone: str = "",
    address: str = "",
    quantity: int = 1,
    email: str = "",
    user=None,
    product_snapshot: Optional[Dict[str, Any]] = None,
) -> Order:
    """
    Create a complete local Assistify order from the chat checkout flow.

    The local PostgreSQL order is the source of truth and is created without
    requiring Shopify. The function also creates one OrderItem and the first
    TrackingUpdate inside the same database transaction.
    """
    snapshot = product_snapshot or {}
    normalized_quantity = _normalize_quantity(quantity)

    clean_phone = str(phone or "").strip()
    clean_address = str(address or "").strip()

    normalized_phone = (
        clean_phone
        .replace("+", "")
        .replace(" ", "")
        .replace("-", "")
        .replace("(", "")
        .replace(")", "")
    )

    if not normalized_phone.isdigit() or not 8 <= len(normalized_phone) <= 15:
        raise ValueError(
            "A valid phone number is required."
        )

    if len(clean_address) < 5:
        raise ValueError(
            "A valid delivery address is required."
        )

    authenticated_user = None

    if (
        user is not None
        and getattr(user, "is_authenticated", False)
    ):
        authenticated_user = user

    clean_email = str(email or "").strip().lower()

    if not clean_email and authenticated_user is not None:
        clean_email = str(
            getattr(authenticated_user, "email", "")
            or ""
        ).strip().lower()

    if not clean_email:
        clean_email = "customer@example.com"

    product = _resolve_local_product(
        product_id=product_id,
        product_snapshot=snapshot,
    )

    if product is not None:
        if product.stock < normalized_quantity:
            raise ValueError(
                f"Product '{product.name}' is out of stock (available: {product.stock})."
            )
        product.stock -= normalized_quantity
        product.save(update_fields=["stock"])
        product_name = product.name
        product_emoji = getattr(product, "emoji", "") or "📦"
        unit_price = _decimal_price(product.price)
    else:
        product_name = str(
            snapshot.get("name")
            or snapshot.get("title")
            or "Chat product"
        ).strip()

        product_emoji = str(
            snapshot.get("emoji")
            or "📦"
        ).strip()

        snapshot_price = snapshot.get("price")

        if snapshot_price in (None, ""):
            raise ValueError(
                "The selected chat product could not be matched to a "
                "local product and has no price."
            )

        unit_price = _decimal_price(snapshot_price)

    subtotal = (
        unit_price * normalized_quantity
    ).quantize(Decimal("0.01"))

    shipping_fee = DEFAULT_SHIPPING_FEE
    total = subtotal + shipping_fee

    order = Order.objects.create(
        user=authenticated_user,
        customer_email=clean_email,
        phone=clean_phone,
        delivery_address=clean_address,
        subtotal=subtotal,
        shipping_fee=shipping_fee,
        total=total,
        payment_method=Order.PaymentMethod.COD,
        status=Order.Status.PLACED,
    )

    OrderItem.objects.create(
        order=order,
        product=product,
        product_name=product_name,
        product_emoji=product_emoji,
        unit_price=unit_price,
        quantity=normalized_quantity,
    )

    TrackingUpdate.objects.create(
        order=order,
        date=timezone.now().date(),
        status=order.get_status_display(),
        location="Warehouse",
    )

    transaction.on_commit(
        lambda: send_order_confirmation(order),
        robust=True,
    )

    return order