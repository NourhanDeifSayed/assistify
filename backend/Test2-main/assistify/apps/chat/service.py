from assistify.apps.products.models import Product, Offer


def search_products(query: str):
    return list(
        (
            Product.objects.filter(is_active=True, name__icontains=query)
            | Product.objects.filter(is_active=True, description__icontains=query)
        )
        .prefetch_related("benefits", "related_products")
        .distinct()[:3]
    )


def get_reply(message: str) -> str:
    lower = message.lower()

    if any(w in lower for w in ["hello", "hi", "hey", "مرحبا", "اهلا", "السلام"]):
        return (
            "👋 Hello! Welcome to MediCare AI. I can help you find medical devices, "
            "check your orders, or answer any questions. What can I do for you today?"
        )

    if any(w in lower for w in ["offer", "discount", "sale", "deal", "عرض", "خصم"]):
        offers = Offer.objects.filter(is_active=True).select_related("product")[:5]
        if not offers:
            return "There are no active offers at the moment. Check back soon! 🛍️"
        lines = ["🏷️ Here are our current offers:\n"]
        for o in offers:
            lines.append(
                f"• {o.product.emoji} **{o.product.name}** — "
                f"{o.discount_percent}% off → {o.discounted_price} EGP "
                f"(was {o.product.price} EGP)"
            )
        return "\n".join(lines)

    if any(w in lower for w in ["track", "order", "delivery", "shipping", "طلب", "شحن", "توصيل"]):
        from assistify.apps.orders.models import Order
        orders = Order.objects.prefetch_related("tracking_updates").order_by("-created_at")[:3]
        if not orders:
            return "No orders found. Place an order first and I'll help you track it! 📦"
        lines = ["📦 Here are your recent orders:\n"]
        for order in orders:
            updates = " → ".join(u.status for u in order.tracking_updates.all())
            lines.append(
                f"• **{order.order_number}** | Status: {order.get_status_display()} | "
                f"Timeline: {updates or 'N/A'} | "
                f"Est. Delivery: {order.estimated_delivery or 'TBD'}"
            )
        return "\n".join(lines)

    if any(w in lower for w in ["payment", "pay", "cash", "card", "دفع", "كارت"]):
        return (
            "💳 We accept two payment methods:\n\n"
            "• **Credit / Debit Card** — Visa, Mastercard\n"
            "• **Cash on Delivery (COD)** — Pay when your order arrives\n\n"
            "Shipping fee is a flat 50 EGP on all orders."
        )

    if any(w in lower for w in ["return", "refund", "exchange", "استرجاع", "استبدال"]):
        return (
            "↩️ Our return policy:\n\n"
            "• Returns accepted within **14 days** of delivery\n"
            "• Item must be unused and in original packaging\n"
            "• Contact support to initiate a return\n\n"
            "We'll process your refund within 5–7 business days."
        )

    products = search_products(message)
    if products:
        lines = [f"🔍 I found {len(products)} product(s) matching your query:\n"]
        for p in products:
            benefits = ", ".join(b.text for b in p.benefits.all()[:3])
            related = p.related_products.filter(is_active=True)[:2]
            related_names = ", ".join(r.name for r in related)
            lines.append(
                f"• {p.emoji} **{p.name}** — {p.price} {p.currency}\n"
                f"  {p.description}\n"
                f"  ✅ {benefits}"
            )
            if related_names:
                lines.append(f"  🔗 Often bought with: {related_names}")
        lines.append("\nWould you like to add any of these to your cart?")
        return "\n".join(lines)

    if any(w in lower for w in ["product", "device", "show", "list", "all", "منتج", "أجهزة"]):
        all_products = Product.objects.filter(is_active=True)
        if not all_products:
            return "No products available right now. Please check back soon!"
        lines = ["🛒 Our medical devices:\n"]
        for p in all_products:
            lines.append(f"• {p.emoji} **{p.name}** — {p.price} {p.currency}: {p.description}")
        lines.append("\nType a product name to get more details!")
        return "\n".join(lines)

    return (
        "🤖 I'm MediCare AI! I can help you with:\n\n"
        "• 🔍 Finding medical devices\n"
        "• 🏷️ Current offers and discounts\n"
        "• 📦 Order tracking\n"
        "• 💳 Payment methods\n"
        "• ↩️ Returns and refunds\n\n"
        "Just type your question!"
    )
