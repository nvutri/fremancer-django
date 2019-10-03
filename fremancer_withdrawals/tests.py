from datetime import date
from django.contrib.auth.models import User
from django.test import TestCase, Client
from rest_framework.test import APIClient

from fremancer_users.models import UserProfile, UserBank
from fremancer_invoices.models import FremancerInvoice
from fremancer_contracts.models import FremancerContract


class WithdrawalsTestCase(TestCase):
    """Testing the handling of withdrawals."""

    def setUp(self):
        self.freelancer = User.objects.create_user(
            username='freelancer@yahoo.com', email='freelancer@yahoo.com'
        )
        self.freelancer_profile = UserProfile.objects.create(
            user=self.freelancer,
            membership='freelancer',
        )
        self.freelancer_bank = UserBank.objects.create(
            user=self.freelancer,
            available=1000
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.freelancer)
        self.withdraw_form = {
            'freelancer': self.freelancer.id,
            'amount': 200.0,
            'fee': 5.0,
            'total_amount': 205.0,
            'method': 'wu',
            'first_name': 'Test',
            'last_name': 'Freelancer',
            'email': self.freelancer.email,
            'phone_number': '12345678',
            'country': 'US',
            'region': 'LA'
        }

    def test_create_new_withdrawal(self):
        """Test creating new withdrawal."""
        response = self.client.post('/api/withdrawals/', self.withdraw_form)
        self.assertEqual(response.status_code, 201, response)

    def test_create_invalid_withdrawal(self):
        """Test creating new withdrawal."""
        withdrawal = self.withdraw_form
        withdrawal['total_amount'] = 1.0
        response = self.client.post('/api/withdrawals/', withdrawal)
        self.assertEqual(response.status_code, 400)
        withdrawal['total_amount'] = 10000.0
        response = self.client.post('/api/withdrawals/', withdrawal)
        self.assertEqual(response.status_code, 400)

    def test_total_withdrawal(self):
        """Test creating new withdrawal."""
        withdrawal = self.withdraw_form
        withdrawal['amount'] = 200.0
        withdrawal['total_amount'] = 205.0
        self.client.post('/api/withdrawals/', withdrawal)
        withdrawal['amount'] = 22.0
        withdrawal['total_amount'] = 27.0
        self.client.post('/api/withdrawals/', withdrawal)
        # Test get Total API.
        response = self.client.get('/api/withdrawals/total/')
        self.assertEqual(response.status_code, 200)
        withdrawal = response.json()
        self.assertEqual(withdrawal.get('total'), 232.0)

    def create_test_invoice(self):
        contract = FremancerContract.objects.create(
            hirer=self.freelancer,
            freelancer=self.freelancer,
            description='Test Contract creation',
            default_payment='card_1AoWMOCaQ7YmitADQPH7cLQq',
            duration='short',
            contract_type='hourly',
            hourly_rate=20.0
        )
        invoice = FremancerInvoice.objects.create(
            hirer=self.freelancer,
            freelancer=self.freelancer,
            total_amount=220,
            total_hours=20,
            paid=True,
            amount=200,
            contract=contract,
        )
        return invoice

    def test_account_available_balance(self):
        """Test getting account available and balance."""
        invoice = self.create_test_invoice()
        withdrawal = self.withdraw_form
        withdrawal['amount'] = 15.0
        withdrawal['total_amount'] = 20.0
        r = self.client.post('/api/withdrawals/', withdrawal)
        self.assertEqual(r.status_code, 201)
        r = self.client.post('/api/withdrawals/', withdrawal)
        self.assertEqual(r.status_code, 201)
        withdrawal['amount'] = 17.0
        withdrawal['total_amount'] = 22.0
        r = self.client.post('/api/withdrawals/', withdrawal)
        self.assertEqual(r.status_code, 201)
        # Test get Total API.
        response = self.client.get('/api/withdrawals/balance/')
        self.assertEqual(response.status_code, 200)
        withdrawal = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(withdrawal.get('balance'), 138.0)
        self.assertEqual(withdrawal.get('available'), 138.0)
        self.assertEqual(withdrawal.get('pending'), 0.0)
        # Create a pending invoice.
        invoice_2 = self.create_test_invoice()
        invoice_2.paid = False
        invoice_2.stripe_charge_status = 'pending'
        invoice_2.save()
        response = self.client.get('/api/withdrawals/balance/')
        self.assertEqual(response.status_code, 200)
        withdrawal = response.json()
        self.assertEqual(withdrawal.get('balance'), 338.0)
        self.assertEqual(withdrawal.get('available'), 138.0)
        self.assertEqual(withdrawal.get('pending'), 200.0)
