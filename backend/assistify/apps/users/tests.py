from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class SecurityRegistrationTests(APITestCase):
    def test_public_registration_ignores_and_blocks_admin_fields(self):
        url = reverse("users:auth-register")
        data = {
            "username": "hacker123",
            "email": "hacker@example.com",
            "password": "password123",
            "password2": "password123",
            "role": "admin",
            "is_staff": True,
            "is_superuser": True,
            "is_admin": True,
        }
        response = self.client.post(url, data)
        # Verify that we reject/block with validation error
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("You cannot specify admin roles or flags", str(response.data))

        # Check if the user was NOT created
        self.assertFalse(User.objects.filter(email="hacker@example.com").exists())

    def test_public_registration_success_as_customer(self):
        url = reverse("users:auth-register")
        data = {
            "username": "customer123",
            "email": "customer@example.com",
            "password": "password123",
            "password2": "password123",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        user = User.objects.get(email="customer@example.com")
        self.assertEqual(user.role, User.Role.CUSTOMER)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)


class AdminUserManagementTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="adminpassword",
            role=User.Role.ADMIN,
        )
        self.staff_admin = User.objects.create_user(
            username="staff_admin",
            email="staff@example.com",
            password="staffpassword",
            role=User.Role.ADMIN,
            is_staff=True,
        )
        self.customer = User.objects.create_user(
            username="customer",
            email="customer@example.com",
            password="customerpassword",
            role=User.Role.CUSTOMER,
        )
        self.list_url = reverse("users:admin-user-list")
        self.detail_url = lambda pk: reverse("users:admin-user-detail", kwargs={"pk": pk})

    def test_unauthenticated_blocked(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_customer_blocked_from_admin_user_endpoints(self):
        self.client.force_authenticate(user=self.customer)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_list_users(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Results should be paginated
        self.assertIn("results", response.data)
        self.assertEqual(len(response.data["results"]), 3)

    def test_admin_can_filter_and_search_users(self):
        self.client.force_authenticate(user=self.admin)
        # Filter by role
        response = self.client.get(self.list_url, {"role": "customer"})
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["email"], "customer@example.com")

        # Search
        response = self.client.get(self.list_url, {"search": "staff"})
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["email"], "staff@example.com")

    def test_deactivate_activate_customer(self):
        self.client.force_authenticate(user=self.admin)
        url = self.detail_url(self.customer.id)
        # Deactivate
        response = self.client.patch(url, {"is_active": False})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.customer.refresh_from_db()
        self.assertFalse(self.customer.is_active)

        # Activate
        response = self.client.patch(url, {"is_active": True})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.customer.refresh_from_db()
        self.assertTrue(self.customer.is_active)

    def test_non_superuser_cannot_grant_superuser_or_staff(self):
        # A staff_admin who is not a superuser tries to elevate the customer
        self.client.force_authenticate(user=self.staff_admin)
        url = self.detail_url(self.customer.id)
        response = self.client.patch(url, {"is_superuser": True})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Only superusers can grant superuser status", str(response.data))

        response = self.client.patch(url, {"is_staff": True})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Only superusers can grant staff status", str(response.data))

        response = self.client.patch(url, {"role": User.Role.ADMIN})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Only superusers can assign the Admin role", str(response.data))
