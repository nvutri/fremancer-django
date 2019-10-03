from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import detail_route
from rest_framework.response import Response

from fremancer_contracts.serializers import ContractSerializer
from fremancer_contracts.models import FremancerContract
from fremancer_users.models import UserProfile


class ContractsViewSet(viewsets.ModelViewSet):
    """API endpoint for contracts handlers."""
    queryset = FremancerContract.objects.all().order_by('-date_created')
    serializer_class = ContractSerializer
    pagination_class = None
    filter_fields = '__all__'

    def get_queryset(self):
        profile = UserProfile.objects.get(user=self.request.user)
        qs = FremancerContract.objects.order_by('-date_created')
        if profile.is_hirer():
            return qs.filter(hirer=self.request.user)
        else:
            return qs.filter(freelancer=self.request.user)

    @detail_route(methods=['post'])
    def accept(self, request, pk):
        contract = FremancerContract.objects.get(pk=pk)
        assert contract.freelancer == request.user
        contract.accepted = True
        contract.save()
        return Response(data={'success': True})

    def create(self, request):
        """Create a new contract."""
        serializer = ContractSerializer(data=request.data)
        if serializer.is_valid():
            contract = serializer.save(hirer=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
