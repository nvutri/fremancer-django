import stripe

from django.conf import settings
from datetime import date
from django.contrib.auth.models import User
from django.test import TestCase, Client
from rest_framework.test import APIClient

from fremancer_users.models import UserProfile, UserBank
from fremancer_contracts.models import FremancerContract
from fremancer_timesheets.models import FremancerTimeSheet
from fremancer_invoices.models import FremancerInvoice

stripe.api_key = settings.STRIPE_KEY


class InvoicesTestCase(TestCase):
    """Testing the handling of invoices."""

    def setUp(self):
        self.hirer = User.objects.create(
            username='hirer@fremancer.com', email='hirer@fremancer.com', password='bar'
        )
        self.hirer_profile = UserProfile.objects.create(
            user=self.hirer,
            membership='hirer',
        )
        self.hirer_bank = UserBank.objects.create(
            user=self.hirer,
            stripe_customer_id='cus_B8yCih3DvwhOR7'
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
        self.contract = FremancerContract.objects.create(
            hirer=self.hirer,
            freelancer=self.freelancer,
            description='Test Contract creation',
            default_payment='card_1AoWMOCaQ7YmitADQPH7cLQq',
            duration='short',
            contract_type='hourly',
            hourly_rate=20.0
        )
        self.timesheet_1 = FremancerTimeSheet.objects.create(
            contract=self.contract,
            start_date=date(2017, 07, 03),
            summary='Test timesheet 1',
            total_hours=22.0,
            total_amount=440.0,
            user=self.freelancer
        )
        self.timesheet_2 = FremancerTimeSheet.objects.create(
            contract=self.contract,
            start_date=date(2017, 07, 10),
            summary='Test timesheet 2',
            total_hours=20.0,
            total_amount=400.0,
            user=self.freelancer
        )
        self.invoice_params = {
            'hirer': self.hirer.id,
            'freelancer': self.freelancer.id,
            'contract': self.contract.id,
            'total_hours': 42.0,
            'amount': 840.0,
            'fee': 24.66,
            'total_amount': 864.66,
            'timesheets': [self.timesheet_1.id, self.timesheet_2.id]
        }

    def test_create_new_invoice(self):
        """Test creating new invoice."""
        invoice_params = self.invoice_params
        response = self.client.post('/api/invoices/', invoice_params)
        self.assertEqual(response.status_code, 201, response)

    def test_update_invoice(self):
        """Test update existing invoice."""
        invoice_params = self.invoice_params
        response_1 = self.client.post('/api/invoices/', invoice_params)
        self.assertEqual(response_1.status_code, 201)
        invoice_params['timesheets'] = [self.timesheet_1.id]
        invoice_params['total_hours'] = 22.0
        invoice_params['total_amount'] = 440.0
        invoice_id = response_1.json().get('id')
        response_2 = self.client.put('/api/invoices/%s/' % invoice_id, invoice_params)
        # No update is allowed.
        self.assertEqual(response_2.status_code, 400)

    def test_wrong_total_hours(self):
        invoice_params = self.invoice_params
        invoice_params['total_hours'] = 41.0
        response = self.client.post('/api/invoices/', invoice_params)
        self.assertEqual(response.status_code, 400, response)

    def test_wrong_amount(self):
        invoice_params = self.invoice_params
        invoice_params['amount'] = 841.0
        response = self.client.post('/api/invoices/', invoice_params)
        self.assertEqual(response.status_code, 400, response)

    def test_over_limit_amount(self):
        invoice_params = self.invoice_params
        invoice_params['amount'] = 10000.5
        response = self.client.post('/api/invoices/', invoice_params)
        self.assertEqual(response.status_code, 400, response)
        self.assertIn('amount', response.json(), response.json())

    def test_pay(self):
        invoice = FremancerInvoice.objects.create(
            hirer=self.hirer,
            freelancer=self.freelancer,
            contract=self.contract,
            total_hours=2.0,
            total_amount=84.0,
        )
        invoice.timesheets.add(self.timesheet_1)
        invoice.timesheets.add(self.timesheet_2)
        response = self.client.post('/api/invoices/%s/pay/' % invoice.id)
        self.assertEqual(response.status_code, 200, response)
        self.assertEqual(response.json().get('status'), 'succeeded')
        paid_invoice = FremancerInvoice.objects.get(pk=invoice.id)
        self.assertTrue(paid_invoice.paid)
        self.assertIsNotNone(paid_invoice.stripe_charge_id)
        self.assertEqual(paid_invoice.stripe_charge_status, 'succeeded')

    def test_get_balance(self):
        response = self.client.post('/api/invoices/', self.invoice_params)
        self.assertEqual(response.status_code, 201, response)
        invoice = response.json()
        response = self.client.post('/api/invoices/%s/pay/' % invoice.get('id'))
        self.assertEqual(response.status_code, 200, response)
        # Test account balance.
        response = self.client.get('/api/invoices/balance/')
        self.assertEqual(response.status_code, 200)
        balance = response.json()
        self.assertEqual(balance.get('total'), 864.66)
        self.assertEqual(balance.get('pending'), 0.0)
        # Test pending payemnt
        invoice = FremancerInvoice.objects.get(id=invoice.get('id'))
        invoice.stripe_charge_status = 'pending'
        invoice.save()
        response = self.client.get('/api/invoices/balance/')
        self.assertEqual(response.status_code, 200)
        balance = response.json()
        self.assertEqual(balance.get('total'), 864.66)
        self.assertEqual(balance.get('pending'), 864.66)

    def test_stripe_webhook(self):
        response = self.client.post('/api/invoices/', self.invoice_params)
        self.assertEqual(response.status_code, 201, response)
        invoice = response.json()
        test_event = {
          "object": {
            "id": invoice.get('stripe_charge_id'),
            "object": 'charge',
            "paid": True,
            "receipt_email": invoice.get('hirer@fremancer.com'),
            "status": "test_status"
          }
        }
        c = APIClient()
        response = c.post('/webhook/', data=test_event, format='json')
        self.assertEqual(response.status_code, 200)
        hooked_invoice = FremancerInvoice.objects.get(id=invoice.get('id'))
        self.assertEqual(hooked_invoice.paid, True)
        self.assertEqual(hooked_invoice.stripe_charge_status, 'test_status')

class PaymentsTestCase(TestCase):

    def setUp(self):
        self.client = APIClient()
        response = self.client.post('/api/users/', {
            'email': 'test_stripe@fremancer.com',
            'password': '12345678',
            'first_name': 'firstN',
            'last_name': 'lastN',
            'membership': 'hirer'
        })
        self.hirer = User.objects.get(username='test_stripe@fremancer.com')
        self.client.force_authenticate(user=self.hirer)

    def test_create_credit_card(self):
        """Test creating first and adding more credit cards."""
        # Create new Stripe payment credit card.
        response = self.client.post('/api/payments/', {
            'id': 'tok_mastercard'
        })
        self.assertEqual(response.status_code, 201, response)
        hirer_bank = UserBank.objects.get(user=self.hirer)
        stripe_id = hirer_bank.stripe_customer_id
        self.assertIsNotNone(stripe_id)
        stripe_user = stripe.Customer.retrieve(stripe_id)
        self.assertEqual(stripe_user.sources.total_count, 1)
        # Add more stripe credit card.
        response = self.client.post('/api/payments/', {
            'id': 'tok_mastercard'
        })
        self.assertEqual(response.status_code, 201, response)
        stripe_user = stripe.Customer.retrieve(stripe_id)
        self.assertEqual(stripe_user.sources.total_count, 2)
        # Remove user from Stripe.
        for customer in stripe.Customer.list().data:
            if customer.email == 'test_stripe@fremancer.com':
                customer.delete()

    def test_create_bank_account(self):
        """Test creating first and adding more credit cards."""
        # Create bank account token.
        token = stripe.Token.create(
          bank_account={
            "country": 'US',
            "currency": 'usd',
            "account_holder_name": 'Matthew Anderson',
            "account_holder_type": 'individual',
            "routing_number": '110000000',
            "account_number": '000123456789'
          },
        )
        # Create new Stripe bank account.
        response = self.client.post('/api/payments/', {
            'id': token.id
        })
        self.assertEqual(response.status_code, 201, response)
        hirer_bank = UserBank.objects.get(user=self.hirer)
        stripe_id = hirer_bank.stripe_customer_id
        self.assertIsNotNone(stripe_id)
        stripe_user = stripe.Customer.retrieve(stripe_id)
        user_sources = stripe_user.sources.all(object="bank_account")
        self.assertEqual(len(user_sources.data), 1)

        # Remove user from Stripe.
        for customer in stripe.Customer.list().data:
            if customer.email == 'test_stripe@fremancer.com':
                customer.delete()

    def test_list_stripe_payment_options(self):
        response = self.client.get('/api/payments/')
        self.assertEqual(response.status_code, 200, response)

    def test_remove_stripe_payment(self):
        # Create a new source.
        response = self.client.post('/api/payments/', {
            'id': 'tok_mastercard'
        })
        self.assertEqual(response.status_code, 201, response)
        # Get all the sources.
        response = self.client.get('/api/payments/')
        card = response.json().get('data')[-1]
        # Remove the latest source.
        response = self.client.delete('/api/payments/%s/' % card.get('id'))
        self.assertEqual(response.status_code, 200, response)
