from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from assistify.apps.products.models import Product, Offer
from assistify.apps.orders.models import Order
from assistify.ml_models.product_recommendation.model import RecommendationModel
import datetime

User = get_user_model()


class ProductManagementTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="adminpassword",
            role=User.Role.ADMIN,
        )
        self.customer = User.objects.create_user(
            username="customer",
            email="customer@example.com",
            password="customerpassword",
            role=User.Role.CUSTOMER,
        )
        self.product = Product.objects.create(
            name="BP Monitor",
            description="Blood pressure monitor",
            price=2500.00,
            stock=10,
            is_active=True,
            category="Devices",
        )
        self.list_url = reverse("products:product-list")
        self.detail_url = lambda pk: reverse("products:product-detail", kwargs={"pk": pk})

    def test_customer_view_only_active_products(self):
        # Create an inactive product
        Product.objects.create(
            name="Old Thermometer",
            description="Mercury thermometer",
            price=150.00,
            stock=5,
            is_active=False,
            category="Devices",
        )
        # Unauthenticated/Customer can list products but only see active ones
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Results is paginated
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["name"], "BP Monitor")

    def test_admin_can_view_all_products(self):
        Product.objects.create(
            name="Old Thermometer",
            description="Mercury thermometer",
            price=150.00,
            stock=5,
            is_active=False,
            category="Devices",
        )
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)

    def test_admin_create_product(self):
        self.client.force_authenticate(user=self.admin)
        data = {
            "name": "Glucometer",
            "description": "Blood glucose monitor",
            "price": 1200.00,
            "stock": 25,
            "category": "Devices",
            "emoji": "🩸",
            "is_active": True,
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Product.objects.filter(name="Glucometer").exists())

    def test_customer_cannot_create_product(self):
        self.client.force_authenticate(user=self.customer)
        data = {
            "name": "Glucometer",
            "description": "Blood glucose monitor",
            "price": 1200.00,
            "stock": 25,
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_update_and_deactivate_product(self):
        self.client.force_authenticate(user=self.admin)
        url = self.detail_url(self.product.id)
        # Update
        response = self.client.patch(url, {"stock": 15, "category": "Home Devices"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 15)
        self.assertEqual(self.product.category, "Home Devices")

        # Deactivate (delete)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.product.refresh_from_db()
        self.assertFalse(self.product.is_active)


class OfferManagementTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="adminpassword",
            role=User.Role.ADMIN,
        )
        self.product = Product.objects.create(
            name="Oximeter",
            description="Pulse oximeter",
            price=1000.00,
            stock=10,
        )
        self.list_url = reverse("products:admin-offer-list")
        self.detail_url = lambda pk: reverse("products:admin-offer-detail", kwargs={"pk": pk})

    def test_offer_validation_prevents_invalid_discount(self):
        self.client.force_authenticate(user=self.admin)
        # Discounted price >= original price should fail
        data = {
            "product": self.product.id,
            "discount_percent": 10,
            "discounted_price": 1100.00,
            "is_active": True,
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("discounted_price", response.data)

        # Expiration date in the past should fail
        data = {
            "product": self.product.id,
            "discount_percent": 10,
            "discounted_price": 900.00,
            "is_active": True,
            "valid_until": str(datetime.date.today() - datetime.timedelta(days=1)),
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("valid_until", response.data)

    def test_offer_crud_by_admin(self):
        self.client.force_authenticate(user=self.admin)
        # Create
        data = {
            "product": self.product.id,
            "discount_percent": 15,
            "discounted_price": 850.00,
            "is_active": True,
            "valid_until": str(datetime.date.today() + datetime.timedelta(days=10)),
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Offer.objects.filter(product=self.product).exists())


class RecommendationStockTests(APITestCase):
    def setUp(self):
        self.active_in_stock = Product.objects.create(
            name="Blood Pressure Monitor Device",
            description="Blood pressure monitor",
            price=2500.00,
            stock=10,
            is_active=True,
        )
        self.active_out_of_stock = Product.objects.create(
            name="Glucose Monitor Device",
            description="Glucose monitor",
            price=1500.00,
            stock=0,
            is_active=True,
        )
        self.inactive_product = Product.objects.create(
            name="Thermometer Device",
            description="Thermometer",
            price=500.00,
            stock=10,
            is_active=False,
        )
        self.recommender = RecommendationModel()

    def test_recommendations_exclude_inactive_and_out_of_stock(self):
        # Predict based on inquiry matching "Device"
        res = self.recommender.predict(query="Device")
        recs = res.get("recommendations", [])
        
        # Should recommend only active_in_stock product
        rec_ids = [r["product_id"] for r in recs]
        self.assertIn(self.active_in_stock.id, rec_ids)
        self.assertNotIn(self.active_out_of_stock.id, rec_ids)
        self.assertNotIn(self.inactive_product.id, rec_ids)
