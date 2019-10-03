from rest_framework import serializers

from fremancer_contracts.models import FremancerContract


class ContractSerializer(serializers.ModelSerializer):
    freelancer_name = serializers.CharField(read_only=True)
    hirer_name = serializers.CharField(read_only=True)
    is_hourly = serializers.BooleanField(read_only=True)

    class Meta:
        model = FremancerContract
        fields = '__all__'
