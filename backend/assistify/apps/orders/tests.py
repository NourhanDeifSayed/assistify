import re
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.core import mail
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from assistify.apps.orders.models import Order, OrderItem, TrackingUpdate
from assistify.apps.orders.services import (
    create_order_from_chat,
    generate_order_tracking_token,
)
from assistify.apps.products.models import Product
from assistify.apps.chat.models import Conversation
from assistify.ml_models.orchestrator import SignalBundle
from assistify.ml_models.state_machine import PurchaseState, StateMachine

User = get_user_model()

class OrderCheckoutFlowTests(TestCase):
    def setUp(self):
        self.product = Product.objects.create(
            name="Blood Pressure Monitor",
            price=Decimal("120.00"),
            stock=10,
            is_active=True,
            emoji="🩺"
        )
        self.customer = User.objects.create_user(
            username="testuser",
            email="user@example.com",
            password="testpassword",
            role=User.Role.CUSTOMER
        )
        self.conv = Conversation.objects.create(user=self.customer)
        self.snapshot = {
            "product_id": self.product.id,
            "name": self.product.name,
            "price": float(self.product.price),
            "emoji": self.product.emoji,
        }

    def _init_bundle(self, message, state=PurchaseState.IDLE):
        bundle = SignalBundle(message=message)
        bundle.language = "en"
        bundle.purchase_state = state
        bundle.last_product_id = self.product.id
        bundle.last_product_snapshot = self.snapshot
        bundle.user_name = self.conv.user_name
        bundle.phone = self.conv.phone
        bundle.email = self.conv.email
        bundle.address = self.conv.address
        bundle.quantity = self.conv.quantity
        return bundle

    def test_new_order_clears_stale_transactional_fields(self):
        self.conv.phone = "01012345678"
        self.conv.email = "stale@example.com"
        self.conv.address = "Stale address road"
        self.conv.quantity = 5
        self.conv.save()

        bundle = self._init_bundle("I want to buy")
        StateMachine.start_purchase_flow(bundle, self.conv)

        self.conv.refresh_from_db()
        self.assertEqual(self.conv.phone, None)
        self.assertEqual(self.conv.email, None)
        self.assertEqual(self.conv.address, None)
        self.assertEqual(self.conv.quantity, None)
        self.assertEqual(self.conv.purchase_state, "awaiting_name")

    def test_complete_checkout_flow_english(self):
        bundle = self._init_bundle("I want to buy a Blood Pressure Monitor")
        handled = StateMachine.start_purchase_flow(bundle, self.conv)
        self.assertTrue(handled)
        self.assertEqual(bundle.purchase_state, PurchaseState.AWAITING_NAME)
        self.assertIn("full name", bundle.response)

        bundle = self._init_bundle("John Doe", PurchaseState.AWAITING_NAME)
        handled = StateMachine.run(bundle, self.conv)
        self.assertTrue(handled)
        self.assertEqual(bundle.purchase_state, PurchaseState.AWAITING_EMAIL)
        self.assertIn("email address", bundle.response)

        bundle = self._init_bundle("john.doe@example.com", PurchaseState.AWAITING_EMAIL)
        handled = StateMachine.run(bundle, self.conv)
        self.assertTrue(handled)
        self.assertEqual(bundle.purchase_state, PurchaseState.AWAITING_PHONE)
        self.assertIn("phone number", bundle.response)

        bundle = self._init_bundle("01011223344", PurchaseState.AWAITING_PHONE)
        handled = StateMachine.run(bundle, self.conv)
        self.assertTrue(handled)
        self.assertEqual(bundle.purchase_state, PurchaseState.AWAITING_ADDRESS)
        self.assertIn("delivery address", bundle.response)

        bundle = self._init_bundle("123 Cairo Main St", PurchaseState.AWAITING_ADDRESS)
        handled = StateMachine.run(bundle, self.conv)
        self.assertTrue(handled)
        self.assertEqual(bundle.purchase_state, PurchaseState.AWAITING_QUANTITY)
        self.assertIn("units", bundle.response)

        bundle = self._init_bundle("2", PurchaseState.AWAITING_QUANTITY)
        handled = StateMachine.run(bundle, self.conv)
        self.assertTrue(handled)
        self.assertEqual(bundle.purchase_state, PurchaseState.READY_TO_ORDER)
        self.assertIn("John Doe", bundle.response)
        self.assertIn("john.doe@example.com", bundle.response)
        self.assertIn("01011223344", bundle.response)
        self.assertIn("123 Cairo Main St", bundle.response)
        self.assertIn("EGP 290.00", bundle.response)

        bundle = self._init_bundle("yes", PurchaseState.READY_TO_ORDER)
        handled = StateMachine.run(bundle, self.conv)
        self.assertFalse(handled)

    def test_complete_checkout_flow_arabic(self):
        self.conv.language = "ar"
        self.conv.save()
        
        bundle = self._init_bundle("عايز اشتري")
        bundle.language = "ar"
        handled = StateMachine.start_purchase_flow(bundle, self.conv)
        self.assertTrue(handled)
        self.assertEqual(bundle.purchase_state, PurchaseState.AWAITING_NAME)
        self.assertIn("اسمك الكامل", bundle.response)

        bundle = self._init_bundle("أحمد محمد", PurchaseState.AWAITING_NAME)
        bundle.language = "ar"
        handled = StateMachine.run(bundle, self.conv)
        self.assertTrue(handled)
        self.assertEqual(bundle.purchase_state, PurchaseState.AWAITING_EMAIL)
        self.assertIn("البريد الإلكتروني", bundle.response)

        bundle = self._init_bundle("ahmed@example.com", PurchaseState.AWAITING_EMAIL)
        bundle.language = "ar"
        handled = StateMachine.run(bundle, self.conv)
        self.assertTrue(handled)
        self.assertEqual(bundle.purchase_state, PurchaseState.AWAITING_PHONE)
        self.assertIn("رقم الموبايل", bundle.response)

        bundle = self._init_bundle("01222334455", PurchaseState.AWAITING_PHONE)
        bundle.language = "ar"
        handled = StateMachine.run(bundle, self.conv)
        self.assertTrue(handled)
        self.assertEqual(bundle.purchase_state, PurchaseState.AWAITING_ADDRESS)
        self.assertIn("عنوان التوصيل", bundle.response)

        bundle = self._init_bundle("الجيزة - شارع الهرم", PurchaseState.AWAITING_ADDRESS)
        bundle.language = "ar"
        handled = StateMachine.run(bundle, self.conv)
        self.assertTrue(handled)
        self.assertEqual(bundle.purchase_state, PurchaseState.AWAITING_QUANTITY)
        self.assertIn("كام قطعة", bundle.response)

        bundle = self._init_bundle("3", PurchaseState.AWAITING_QUANTITY)
        bundle.language = "ar"
        handled = StateMachine.run(bundle, self.conv)
        self.assertTrue(handled)
        self.assertEqual(bundle.purchase_state, PurchaseState.READY_TO_ORDER)
        self.assertIn("أحمد محمد", bundle.response)
        self.assertIn("ahmed@example.com", bundle.response)
        self.assertIn("01222334455", bundle.response)
        self.assertIn("شارع الهرم", bundle.response)
        self.assertIn("410", bundle.response)

        bundle = self._init_bundle("تأكيد", PurchaseState.READY_TO_ORDER)
        bundle.language = "ar"
        handled = StateMachine.run(bundle, self.conv)
        self.assertFalse(handled)

    def test_invalid_email_rejected(self):
        bundle = self._init_bundle("invalid-email-address", PurchaseState.AWAITING_EMAIL)
        handled = StateMachine.run(bundle, self.conv)
        self.assertTrue(handled)
        self.assertEqual(bundle.purchase_state, PurchaseState.AWAITING_EMAIL)
        self.assertIn("Invalid email", bundle.response)

    def test_invalid_phone_rejected(self):
        bundle = self._init_bundle("01012345", PurchaseState.AWAITING_PHONE)
        handled = StateMachine.run(bundle, self.conv)
        self.assertTrue(handled)
        self.assertEqual(bundle.purchase_state, PurchaseState.AWAITING_PHONE)
        self.assertIn("valid Egyptian phone", bundle.response)

    def test_zero_and_negative_quantities_rejected(self):
        bundle = self._init_bundle("0", PurchaseState.AWAITING_QUANTITY)
        handled = StateMachine.run(bundle, self.conv)
        self.assertTrue(handled)
        self.assertEqual(bundle.purchase_state, PurchaseState.AWAITING_QUANTITY)
        
        bundle = self._init_bundle("-5", PurchaseState.AWAITING_QUANTITY)
        handled = StateMachine.run(bundle, self.conv)
        self.assertTrue(handled)
        self.assertEqual(bundle.purchase_state, PurchaseState.AWAITING_QUANTITY)

    def test_non_integer_quantity_rejected(self):
        bundle = self._init_bundle("abc", PurchaseState.AWAITING_QUANTITY)
        handled = StateMachine.run(bundle, self.conv)
        self.assertTrue(handled)
        self.assertEqual(bundle.purchase_state, PurchaseState.AWAITING_QUANTITY)

    def test_quantity_exceeding_stock_rejected(self):
        bundle = self._init_bundle("11", PurchaseState.AWAITING_QUANTITY)
        handled = StateMachine.run(bundle, self.conv)
        self.assertTrue(handled)
        self.assertEqual(bundle.purchase_state, PurchaseState.AWAITING_QUANTITY)
        self.assertIn("not available", bundle.response)

    def test_incomplete_checkout_resumes_correctly(self):
        self.conv.user_name = "John Resumed"
        self.conv.purchase_state = PurchaseState.AWAITING_EMAIL.value
        self.conv.save()

        bundle = self._init_bundle("I want to buy")
        handled = StateMachine.start_purchase_flow(bundle, self.conv)
        self.assertTrue(handled)
        self.assertEqual(bundle.purchase_state, PurchaseState.AWAITING_EMAIL)
        self.assertIn("email address", bundle.response)

    def test_cancellation_clears_pending_checkout(self):
        self.conv.user_name = "Cancel User"
        self.conv.phone = "01011223344"
        self.conv.email = "cancel@example.com"
        self.conv.purchase_state = PurchaseState.READY_TO_ORDER.value
        self.conv.save()

        bundle = self._init_bundle("cancel", PurchaseState.READY_TO_ORDER)
        handled = StateMachine.run(bundle, self.conv)
        self.assertTrue(handled)
        self.assertEqual(bundle.purchase_state, PurchaseState.IDLE)
        
        self.conv.refresh_from_db()
        self.assertEqual(self.conv.phone, None)
        self.assertEqual(self.conv.email, None)
        self.assertEqual(self.conv.address, None)
        self.assertEqual(self.conv.quantity, None)
        self.assertEqual(self.conv.purchase_state, "idle")

    def test_successful_confirmation_creates_order_and_order_item(self):
        mail.outbox = []

        order = create_order_from_chat(
            product_id=self.product.id,
            phone="01011223344",
            address="123 Road Cairo",
            quantity=2,
            email="test@example.com",
            user=self.customer,
            product_snapshot=self.snapshot,
            customer_name="Ahmed Ali"
        )

        self.assertIsNotNone(order)
        self.assertEqual(order.customer_name, "Ahmed Ali")
        self.assertEqual(order.customer_email, "test@example.com")
        self.assertEqual(order.phone, "01011223344")
        self.assertEqual(order.delivery_address, "123 Road Cairo")
        self.assertEqual(order.subtotal, Decimal("240.00"))
        self.assertEqual(order.total, Decimal("290.00"))
        
        self.assertEqual(order.items.count(), 1)
        item = order.items.first()
        self.assertEqual(item.product, self.product)
        self.assertEqual(item.quantity, 2)
        self.assertEqual(item.unit_price, Decimal("120.00"))

        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 8)

    def test_saved_order_visible_in_admin_queryset(self):
        order = create_order_from_chat(
            product_id=self.product.id,
            phone="01011223344",
            address="123 Road Cairo",
            quantity=1,
            email="admin@example.com",
            user=self.customer,
            product_snapshot=self.snapshot,
            customer_name="Admin Visible User"
        )
        all_orders = Order.objects.all()
        self.assertIn(order, all_orders)

    def test_confirmation_email_sent_using_locmem(self):
        mail.outbox = []
        from assistify.apps.orders.email_service import send_order_confirmation
        
        order = create_order_from_chat(
            product_id=self.product.id,
            phone="01011223344",
            address="123 Road Cairo",
            quantity=1,
            email="confirm@example.com",
            user=self.customer,
            product_snapshot=self.snapshot,
            customer_name="Confirm Email User"
        )

        sent = send_order_confirmation(order)
        self.assertTrue(sent)
        self.assertEqual(len(mail.outbox), 1)
        
        sent_email = mail.outbox[0]
        self.assertEqual(sent_email.subject, f"Order Confirmation - {order.order_number}")
        self.assertIn("confirm@example.com", sent_email.to)
        self.assertIn("Confirm Email User", sent_email.body)
        self.assertIn(order.order_number, sent_email.body)
        self.assertIn("Blood Pressure Monitor", sent_email.body)
        self.assertIn("120.00 EGP", sent_email.body)
        self.assertIn("123 Road Cairo", sent_email.body)

    def test_email_failure_does_not_delete_saved_order(self):
        order = create_order_from_chat(
            product_id=self.product.id,
            phone="01011223344",
            address="123 Road Cairo",
            quantity=1,
            email="fail@example.com",
            user=self.customer,
            product_snapshot=self.snapshot,
            customer_name="Fail Email User"
        )

        from unittest.mock import patch
        with patch('django.core.mail.EmailMultiAlternatives.send', side_effect=Exception("SMTP Connection Error")):
            from assistify.apps.orders.email_service import send_order_confirmation
            with self.assertRaises(Exception):
                send_order_confirmation(order)
            
            self.assertTrue(Order.objects.filter(pk=order.pk).exists())

    def test_database_failure_does_not_save_partial_order(self):
        with self.assertRaises(Exception):
            with transaction.atomic():
                create_order_from_chat(
                    product_id=self.product.id,
                    phone="invalid",
                    address="Cairo",
                    quantity=1,
                    email="dbfail@example.com",
                    user=self.customer,
                    product_snapshot=self.snapshot,
                    customer_name="DB Fail"
                )
        
        self.assertEqual(Order.objects.filter(customer_email="dbfail@example.com").count(), 0)

    def test_duplicate_confirmation_retries_idempotency(self):
        order = create_order_from_chat(
            product_id=self.product.id,
            phone="01011223344",
            address="123 Road Cairo",
            quantity=1,
            email="dup@example.com",
            user=self.customer,
            product_snapshot=self.snapshot,
            customer_name="Dup User"
        )
        self.assertEqual(Order.objects.filter(customer_email="dup@example.com").count(), 1)
        
        token = generate_order_tracking_token(order)
        self.assertIsNotNone(token)


class OrderWebAPITests(APITestCase):
    def setUp(self):
        self.product = Product.objects.create(
            name="Blood Pressure Monitor",
            price=Decimal("120.00"),
            stock=10,
            is_active=True,
            emoji="🩺"
        )
        self.customer = User.objects.create_user(
            username="apiuser",
            email="apiuser@example.com",
            password="apipassword",
            role=User.Role.CUSTOMER
        )
        self.url = reverse("orders:order-placement")

    @override_settings(
        EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend"
    )
    def test_place_order_via_api_sends_email(self):
        mail.outbox = []
        self.client.force_authenticate(user=self.customer)
        data = {
            "customer_name": "API Customer",
            "customer_email": "apiorder@example.com",
            "delivery_address": "123 API Road, Cairo",
            "phone": "01011223344",
            "items": [
                {
                    "product_id": self.product.id,
                    "quantity": 2
                }
            ]
        }
        
        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.post(self.url, data, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        order = Order.objects.get(customer_email="apiorder@example.com")
        self.assertEqual(order.customer_name, "API Customer")
        self.assertEqual(order.items.first().quantity, 2)
        
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("apiorder@example.com", mail.outbox[0].to)