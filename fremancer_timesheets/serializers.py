from django.core.exceptions import ValidationError
from rest_framework import serializers

from fremancer_timesheets.models import FremancerTimeSheet, FremancerDailySheet
from fremancer_contracts.models import FremancerContract


class TimeSheetSerializer(serializers.ModelSerializer):
    contract_title = serializers.CharField(read_only=True)
    status = serializers.CharField(read_only=True)

    def validate_total_hours(self, total_hours):
        contract = FremancerContract.objects.get(pk=self.initial_data.get('contract'))
        if contract.is_hourly() and total_hours > contract.max_weekly_hours:
            raise ValidationError(
                'Invalid Total Hours: %s - Max: %s' % (
                    total_hours,
                    contract.max_weekly_hours)
            )
        return total_hours

    class Meta:
        model = FremancerTimeSheet
        fields = '__all__'


class DailySheetSerializer(serializers.ModelSerializer):

    class Meta:
        model = FremancerDailySheet
        fields = '__all__'
