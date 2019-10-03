from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.decorators import detail_route, list_route
from rest_framework.response import Response

from fremancer_invoices.models import FremancerInvoice
from fremancer_users.models import UserBank
from fremancer_withdrawals.serializers import WithdrawalSerializer
from fremancer_withdrawals.models import FremancerWithdrawal


class WithdrawalsViewSet(viewsets.ModelViewSet):
    """API endpoint for withdrawals handlers."""
    queryset = FremancerWithdrawal.objects.all().order_by('-date_created')
    serializer_class = WithdrawalSerializer
    filter_fields = '__all__'

    def get_queryset(self):
        return FremancerWithdrawal.objects.filter(freelancer=self.request.user).order_by('-date_created')

    def update(self, request, pk):
        return Response(
            data={'error': 'Unauthorized Request'},
            status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk):
        return Response(
            data={'error': 'Unauthorized Request'},
            status=status.HTTP_400_BAD_REQUEST)

    def total_withdrawal(self, request):
        """Calculate total withdrawal."""
        qs = self.get_queryset()
        return sum([withdraw.total_amount for withdraw in qs.exclude(cancel=True)])

    @list_route(methods=['get'])
    def total(self, request):
        """Caculate the total of withdrawal on an individual."""
        total = self.total_withdrawal(request)
        return Response({'total': total})

    @list_route(methods=['get'])
    def balance(self, request):
        """Calculate account balance and available."""
        # First calculate total and pending amount.
        total = pending = 0
        for invoice in FremancerInvoice.objects.filter(freelancer=self.request.user):
            total += invoice.amount
            if not invoice.paid or invoice.stripe_charge_status == 'pending':
                pending += invoice.amount
        # Calculate withdrawal already amount.
        withdrawal = self.total_withdrawal(request)
        balance = total - withdrawal
        available = balance - pending
        # Save balance and available amount to user bank.
        bank, _ = UserBank.objects.get_or_create(user=self.request.user)
        bank.balance = balance
        bank.available = available
        bank.save()
        return Response({
            'total': total,
            'balance': balance,
            'withdrawal': withdrawal,
            'available': available,
            'pending': pending
        })
