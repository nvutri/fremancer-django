from decimal import Decimal
from django.core.exceptions import ValidationError
from rest_framework import serializers

from fremancer_users.models import UserBank
from fremancer_withdrawals.models import FremancerWithdrawal


class WithdrawalSerializer(serializers.ModelSerializer):
    method_name = serializers.SerializerMethodField()
    status_title = serializers.SerializerMethodField()

    class Meta:
        model = FremancerWithdrawal
        fields = '__all__'

    def get_method_name(self, item):
        return item.get_method_display()

    def get_status_title(self, item):
        return item.get_status_display()

    def validate_total_amount(self, total_amount):
        """Validate total amount to be smaller than what the account has."""
        bank = UserBank.objects.get(user=self.initial_data.get('freelancer'))
        if total_amount > bank.available:
            raise ValidationError(
                'Invalid Total Amount: %s - Balance: %s' % (
                    total_amount, bank.available)
            )
        return total_amount
