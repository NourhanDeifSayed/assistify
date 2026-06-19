from django.conf import settings
from django.core.mail import EmailMultiAlternatives


def send_order_confirmation(order):
    recipient = order.customer_email

    if not recipient and order.user:
        recipient = order.user.email

    if not recipient:
        return False

    item_lines = []

    for item in order.items.all():
        item_lines.append(
            f"- {item.product_name} x{item.quantity} "
            f"= {item.line_total} EGP"
        )

    items_text = "\n".join(item_lines)

    subject = f"Order Confirmation - {order.order_number}"

    body = (
        f"Hello {order.customer_name},\n\n"
        "Thank you for ordering from Assistify.\n\n"
        f"Order number: {order.order_number}\n"
        f"Status: {order.get_status_display()}\n"
        f"Payment method: {order.get_payment_method_display()}\n\n"
        f"Items:\n{items_text}\n\n"
        f"Subtotal: {order.subtotal} EGP\n"
        f"Shipping fee: {order.shipping_fee} EGP\n"
        f"Total: {order.total} EGP\n\n"
        f"Delivery address: {order.delivery_address}\n"
        f"Phone: {order.phone}\n\n"
        "Keep your order number to track your shipment."
    )

    email = EmailMultiAlternatives(
        subject=subject,
        body=body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[recipient],
    )

    email.send(fail_silently=False)

    return True