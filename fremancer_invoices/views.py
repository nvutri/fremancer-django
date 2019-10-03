import stripe

from decimal import Decimal
from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import detail_route, list_route
from rest_framework.response import Response

from fremancer_invoices.serializers import InvoiceSerializer
from fremancer_invoices.models import FremancerInvoice
from fremancer_users.models import UserProfile, UserBank

stripe.api_key = settings.STRIPE_KEY
STRIPE_CREDIT_PERCENTAGE = Decimal(0.029)  # 2.9%.
STRIPE_CREDIT_FEE = Decimal(0.30)  # 30 cents.
STRIPE_ACH_FEE = Decimal(5.0)  # 5 dollars.
SOURCE_SPLIT_CHAR = '_'


class InvoicesViewSet(viewsets.ModelViewSet):
    """API endpoint for invoices handlers."""
    queryset = FremancerInvoice.objects.all().order_by('-date_created')
    serializer_class = InvoiceSerializer

    def get_queryset(self):
        """Pre filter queryset."""
        profile = UserProfile.objects.get(user=self.request.user)
        if profile.is_freelancer():
            return FremancerInvoice.objects.filter(freelancer=self.request.user).order_by('-date_created')
        else:
            return FremancerInvoice.objects.filter(hirer=self.request.user).order_by('-date_created')

    def get_source_type(self, default_payment):
        if default_payment.split(SOURCE_SPLIT_CHAR):
            return default_payment.split(SOURCE_SPLIT_CHAR)[0]
        source = stripe.Source.retrieve(default_payment)
        return source.object

    def calculate_fee(self, default_payment, amount):
        source = self.get_source_type(default_payment)
        if 'card' in source:
            return amount * STRIPE_CREDIT_PERCENTAGE + STRIPE_CREDIT_FEE
        else:
            return STRIPE_ACH_FEE

    def update_invoice_status(self, invoice):
        charge = stripe.Charge.retrieve(invoice.stripe_charge_id)
        invoice.paid = charge.paid
        invoice.stripe_charge_status = charge.status
        invoice.save()
        return invoice

    def create(self, request):
        """Create a new invoice."""
        serializer = InvoiceSerializer(data=request.data)
        if serializer.is_valid():
            invoice = serializer.save(freelancer=request.user)
            invoice.fee = self.calculate_fee(invoice.contract.default_payment, invoice.amount)
            invoice.total_amount = invoice.amount + invoice.fee
            invoice.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        queryset = self.get_queryset()
        invoice = get_object_or_404(queryset, pk=pk)
        if invoice.stripe_charge_id and not invoice.paid:
            invoice = self.update_invoice_status(invoice)
        serializer = InvoiceSerializer(invoice)
        return Response(serializer.data)

    def update(self, request, pk):
        return Response(
            data={'error': 'Unauthorized Request'},
            status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk):
        return Response(
            data={'error': 'Unauthorized Request'},
            status=status.HTTP_400_BAD_REQUEST)

    def create_metadata(self, invoice):
        """Create metadata for Stripe."""
        metadata = {
            'contract': invoice.contract.id,
            'hours': invoice.total_hours
        }
        index = 0
        for ts in invoice.timesheets.all():
            metadata['timesheet_%s_id' % index] = ts.id
            metadata['timesheet_%s_hours' % index] = ts.total_hours
            metadata['timesheet_%s_amount' % index] = ts.total_amount
            index += 1
        return metadata

    @detail_route(methods=['post'])
    def pay(self, request, pk):
        """Pay stub for owner."""
        invoice = FremancerInvoice.objects.get(pk=pk)
        assert not invoice.paid
        try:
            bank = UserBank.objects.get(user=request.user)
            charge = stripe.Charge.create(
                amount=int(invoice.total_amount * 100),
                currency='usd',
                customer=bank.stripe_customer_id,
                source=invoice.contract.default_payment,
                description='Charge for %s in %s hours' % (
                    invoice.freelancer, invoice.total_hours
                ),
                metadata=self.create_metadata(invoice)
            )
        except Exception as e:
            return Response(data=str(e), status=status.HTTP_400_BAD_REQUEST)
        else:
            invoice.paid = charge.paid
            invoice.stripe_charge_id = charge.id
            invoice.stripe_charge_status = charge.status
            invoice.save()
            return Response(charge)

    @list_route(methods=['get'])
    def balance(self, request):
        """Caculate the total of paid amount on an individual."""
        total = 0
        pending = 0
        for invoice in self.get_queryset():
            total += invoice.total_amount
            if invoice.stripe_charge_status == 'pending':
                pending += invoice.total_amount
        return Response({
            'total': total,
            'pending': pending
        })


class PaymentsViewSet(viewsets.ViewSet):
    """API endpoint for handling payments managements."""

    def create(self, request):
        """Create a user account at Stripe with payment info."""
        bank, _ = UserBank.objects.get_or_create(user=request.user)
        profile = UserProfile.objects.get(user=request.user)
        try:
            if not bank.stripe_customer_id:
                customer = stripe.Customer.create(
                    source=request.POST.get('id'),
                    email=request.user.email,
                    description=profile.membership
                )
                bank.stripe_customer_id = customer.id
                bank.save()
                if customer.sources.data:
                    card = customer.sources.data[0]
            else:
                customer = stripe.Customer.retrieve(bank.stripe_customer_id)
                card = customer.sources.create(card=request.POST.get('id'))
                customer.save()
            if card.object == 'bank_account':
                card.verify(amounts=[32, 45])
        except Exception as e:
            return Response(data=str(e), status=400)
        else:
            return Response({'id': card.id}, status=status.HTTP_201_CREATED)

    def list(self, request):
        """List all payments associatd to a user."""
        bank, _ = UserBank.objects.get_or_create(user=request.user)
        payments = []
        if bank.stripe_customer_id:
            customer = stripe.Customer.retrieve(bank.stripe_customer_id)
            for source in customer.sources:
                source_data = {
                    'id': source.id,
                    'last4': source.last4,
                    'object': source.object
                }
                if source.object == 'card':
                    source_data['brand'] = source.brand
                    source_data['exp'] = '%s/%s' % (source.exp_month, source.exp_year)
                    source_data['name'] = source.name
                else:
                    source_data['brand'] = source.bank_name
                    source_data['exp'] = ''
                    source_data['name'] = source.account_holder_name
                payments.append(source_data)
        return Response({
            'data': payments,
            'stripe_id': bank.stripe_customer_id
        })

    def destroy(self, request, pk):
        """Destroy associatd to a user."""
        bank = UserBank.objects.get(user=request.user)
        if bank.stripe_customer_id:
            customer = stripe.Customer.retrieve(bank.stripe_customer_id)
            customer.sources.retrieve(pk).delete()
            return Response({'success': True})
        else:
            return Response(data='Invalid Request', status=400)
