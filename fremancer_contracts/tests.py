from django.contrib.auth.models import User
from django.test import TestCase, Client
from rest_framework.test import APIClient

from fremancer_users.models import UserProfile


class ContractsTestCase(TestCase):
    """Testing the handling of contracts."""

    def setUp(self):
        self.hirer = User.objects.create(
            username='hirer@yahoo.com', email='hirer@yahoo.com', password='bar'
        )
        self.hirer_profile = UserProfile.objects.create(
            user=self.hirer,
            membership='hirer'
        )

        self.freelancer = User.objects.create_user(
            username='freelancer@yahoo.com', email='freelancer@yahoo.com'
        )
        self.freelancer_profile = UserProfile.objects.create(
            user=self.freelancer,
            membership='freelancer'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.hirer)

    def test_create_new_contract(self):
        """Test creating new contract."""
        response = self.client.post('/api/contracts/', {
            'title': 'Test Contract Title',
            'hirer': self.hirer.id,
            'freelancer': self.freelancer.id,
            'description': 'Test Contract creation',
            'duration': 'short',
            'contract_type': 'hourly',
            'default_payment': 'test_master_card',
            'hourly_rate': 20.0
        })
        self.assertEqual(response.status_code, 201, response)
