from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from assistify.apps.support.models import SupportTicket, FAQEntry
import datetime

User = get_user_model()


class SupportTicketTests(APITestCase):
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
        self.ticket = SupportTicket.objects.create(
            user=self.customer,
            issue_type=SupportTicket.IssueType.OTHER,
            description="My order was damaged during delivery.",
            status=SupportTicket.Status.OPEN,
            priority=SupportTicket.Priority.MEDIUM,
        )
        self.list_url = reverse("support:ticket-list-create")
        self.reply_url = lambda number: reverse("support:ticket-reply", kwargs={"ticket_number": number})

    def test_customer_only_lists_their_own_tickets(self):
        # Create a ticket for another user
        other_user = User.objects.create_user(
            username="other",
            email="other@example.com",
            password="otherpassword",
        )
        SupportTicket.objects.create(
            user=other_user,
            description="Other user issue description.",
        )

        self.client.force_authenticate(user=self.customer)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["ticket_number"], self.ticket.ticket_number)

    def test_admin_can_reply_and_resolve_ticket(self):
        self.client.force_authenticate(user=self.admin)
        url = self.reply_url(self.ticket.ticket_number)
        
        # Admin replies and marks resolved
        data = {
            "response": "We have processed a refund for your damaged item.",
            "status": SupportTicket.Status.RESOLVED,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.admin_response, "We have processed a refund for your damaged item.")
        self.assertEqual(self.ticket.status, SupportTicket.Status.RESOLVED)
        self.assertIsNotNone(self.ticket.resolved_at)
        self.assertEqual(self.ticket.assigned_to, self.admin)


class FAQEntryTests(APITestCase):
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
        self.published_faq = FAQEntry.objects.create(
            question="How do I track my order?",
            answer="Use the tracking page in the navbar.",
            category="Shipping",
            is_published=True,
        )
        self.unpublished_faq = FAQEntry.objects.create(
            question="Internal secret question",
            answer="Secret answer.",
            category="Secret",
            is_published=False,
        )
        self.list_url = reverse("support:faq-list-create")

    def test_customer_only_sees_published_faqs(self):
        self.client.force_authenticate(user=self.customer)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["question"], self.published_faq.question)

    def test_admin_sees_all_faqs(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)
