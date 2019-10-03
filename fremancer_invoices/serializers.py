from django.core.exceptions import ValidationError
from rest_framework import serializers

from fremancer_contracts.serializers import ContractSerializer
from fremancer_invoices.models import FremancerInvoice
from fremancer_timesheets.models import FremancerTimeSheet
from fremancer_timesheets.serializers import TimeSheetSerializer


class InvoiceSerializer(serializers.ModelSerializer):

    status = serializers.CharField(read_only=True)
    pending = serializers.BooleanField(read_only=True)
    contract_data = ContractSerializer(read_only=True)
    timesheets_data = TimeSheetSerializer(read_only=True, many=True)

    class Meta:
        model = FremancerInvoice
        fields = '__all__'

    def validate(self, data):
        """Validate invoice data."""
        total_hours = 0
        amount = 0
        for timesheet in data.get('timesheets'):
            total_hours += timesheet.total_hours
            amount += timesheet.total_amount
        if total_hours != data.get('total_hours'):
            raise ValidationError(
                'Invalid Total Hours: %s' % data.get('total_hours'))
        if amount != data.get('amount'):
            raise ValidationError(
                'Invalid Amount: %s' % data.get('amount'))
        return data
