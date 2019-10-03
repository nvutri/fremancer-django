from datetime import timedelta, datetime

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import list_route
from rest_framework.response import Response

from fremancer_contracts.models import FremancerContract
from fremancer_contracts.serializers import ContractSerializer
from fremancer_timesheets.serializers import TimeSheetSerializer, DailySheetSerializer
from fremancer_timesheets.models import FremancerTimeSheet, FremancerDailySheet
from fremancer_users.models import UserProfile


class TimeSheetsViewSet(viewsets.ModelViewSet):
    """API endpoint for contracts handlers."""
    queryset = FremancerTimeSheet.objects.all().order_by('-date_changed')
    serializer_class = TimeSheetSerializer
    filter_fields = ('contract', 'user')
    DAYS_IN_WEEK = 7

    def get_queryset(self):
        """Pre filter queryset."""
        profile = UserProfile.objects.get(user=self.request.user)
        if profile.is_freelancer():
            return FremancerTimeSheet.objects.filter(user=self.request.user).order_by('-date_changed')
        else:
            contracts = FremancerContract.objects.filter(hirer=self.request.user)
            return FremancerTimeSheet.objects.filter(contract__in=contracts)

    def retrieve(self, request, pk):
        """Retrieve an instance."""
        qs = self.get_queryset()
        timesheet = get_object_or_404(qs, pk=pk)
        freelancer = timesheet.contract.freelancer
        hirer = timesheet.contract.hirer
        if self.request.user not in [freelancer, hirer]:
            return Response(data={'error': 'Unauthorized Request'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = TimeSheetSerializer(timesheet)
        data = serializer.data
        # Get Contract Data.
        contract_serializer = ContractSerializer(timesheet.contract)
        data['contract'] = contract_serializer.data
        # Gather Daily Sheets data.
        data['daily_sheets'] = []
        for daily_sheet in self.get_daily_sheets(freelancer, timesheet):
            data['daily_sheets'].append(DailySheetSerializer(daily_sheet).data)
        # Get Reference of Previous and Next Timesheet.
        data['prev_timesheet'] = data['next_timesheet'] = None
        # Get or Create Timesheet of previous week.
        prev_report_date = timesheet.start_date - timedelta(days=7)
        if prev_report_date > timesheet.contract.date_created.date():
            prev_timesheet, created = FremancerTimeSheet.objects.get_or_create(
                user=freelancer,
                contract=timesheet.contract,
                start_date=prev_report_date
            )
            data['prev_timesheet'] = prev_timesheet.id
        # Get or Create Timesheet of next week.
        next_report_date = timesheet.start_date + timedelta(days=7)
        if next_report_date < datetime.now().date():
            next_timesheet, created = FremancerTimeSheet.objects.get_or_create(
                user=freelancer,
                contract=timesheet.contract,
                start_date=next_report_date
            )
            data['next_timesheet'] = next_timesheet.id
        return Response(data)

    def get_daily_sheets(self, freelancer, timesheet):
        """Create daily sheets for a timesheet."""
        daily_sheets = []
        for date_delta in range(self.DAYS_IN_WEEK):
            instance, created = FremancerDailySheet.objects.get_or_create(
                timesheet=timesheet,
                report_date=timesheet.start_date + timedelta(date_delta),
                user=freelancer
            )
            daily_sheets.append(instance)
        return daily_sheets

    def create(self, request):
        """Create a new timesheet with all related daily sheets."""
        serializer = TimeSheetSerializer(data=request.data)
        if serializer.is_valid():
            timesheet = serializer.save(user=request.user)
            self.get_daily_sheets(request.user, timesheet)
            if timesheet.contract.is_wage():
                timesheet.total_amount = timesheet.contract.wage_amount
                timesheet.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @list_route(methods=['get'])
    def unpaid(self, request):
        """Get a list of not-invoiced timesheets."""
        qs = FremancerTimeSheet.objects
        if self.request.query_params.get('contract'):
            qs = qs.filter(contract=self.request.query_params.get('contract'))
        data = []
        for timesheet in qs.filter(fremancer_invoice__isnull=True):
            serializer = TimeSheetSerializer(timesheet)
            data.append(serializer.data)
        return Response(data)


class DailySheetsViewSet(viewsets.ModelViewSet):
    """API endpoint for contracts handlers."""
    queryset = FremancerDailySheet.objects.all().order_by('-report_date')
    serializer_class = DailySheetSerializer
    filter_fields = ('timesheet', 'user')

    def get_queryset(self):
        """Pre filter queryset."""
        return FremancerDailySheet.objects.filter(user=self.request.user).order_by('-report_date')
