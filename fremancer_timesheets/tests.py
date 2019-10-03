from datetime import date
from django.contrib.auth.models import User
from django.test import TestCase, Client
from rest_framework.test import APIClient

from fremancer_users.models import UserProfile
from fremancer_contracts.models import FremancerContract
from fremancer_timesheets.models import FremancerTimeSheet, FremancerDailySheet


class TimeSheetsTestCase(TestCase):
    """Testing the handling of timesheets."""

    def setUp(self):
        self.hirer = User.objects.create(
            username='hirer@yahoo.com',
            email='hirer@yahoo.com',
            password='bar'
        )
        self.hirer_profile = UserProfile.objects.create(
            user=self.hirer,
            membership='hirer'
        )
        self.freelancer = User.objects.create(
            username='freelancer@yahoo.com',
            email='freelancer@yahoo.com'
        )
        self.freelancer_profile = UserProfile.objects.create(
            user=self.freelancer,
            membership='freelancer'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.freelancer)
        self.contract = FremancerContract.objects.create(
            hirer=self.hirer,
            freelancer=self.freelancer,
            description='Test Contract creation',
            duration='short',
            contract_type='hourly',
            hourly_rate=20.0,
            max_weekly_hours=30
        )
        self.timesheet = FremancerTimeSheet.objects.create(
            contract=self.contract,
            start_date=date(2017, 07, 03),
            summary='Test timesheet',
            total_hours=20.0,
            total_amount=400.0,
            user=self.freelancer
        )

    def test_create_new_timesheet(self):
        """Test creating new timesheet."""
        response = self.client.post('/api/timesheets/', {
            'contract': self.contract.id,
            'start_date': '2017-07-10',
            'summary': 'Test TimeSheet',
            'total_hours': 20.0,
            'total_amount': 400.0,
            'user': self.freelancer.id
        })
        self.assertEqual(response.status_code, 201, response)
        res = response.json()
        timesheet = FremancerTimeSheet.objects.get(pk=res.get('id'))
        # Count number of daily sheets to match the time sheet.
        self.assertEqual(FremancerDailySheet.objects.filter(timesheet=timesheet).count(), 7)
        for daily_sheet in FremancerDailySheet.objects.filter(timesheet=timesheet):
            self.assertGreaterEqual(daily_sheet.report_date, timesheet.start_date)

    def test_create_over_weekly_hours(self):
        response = self.client.post('/api/timesheets/', {
            'contract': self.contract.id,
            'start_date': '2017-07-10',
            'summary': 'Test TimeSheet',
            'total_hours': self.contract.max_weekly_hours + 10.0
            'total_amount': 400.0,
        })
        self.assertEqual(response.status_code, 400, response)

    def test_create_daily_timesheet(self):
        """Test creating a regular daily timesheet."""
        response = self.client.post('/api/dailysheets/', {
            'report_date': '2017-07-04',
            'summary': 'Test daily',
            'hours': 5.5,
            'timesheet': self.timesheet.id,
            'user': self.freelancer.id
        })
        self.assertEqual(response.status_code, 201, response)

    def test_create_wrong_day_timesheet(self):
        """Test creating new timesheet."""
        timesheet_params = {
            'contract': self.contract.id,
            'start_date': '2017-07-05',  # Not a Monday.
            'summary': 'Test TimeSheet',
            'total_hours': 20.0,
            'total_amount': 400.0,
            'user': self.freelancer.id
        }
        response = self.client.post('/api/timesheets/', timesheet_params)
        self.assertEqual(response.status_code, 400, response)
        self.assertIn('start_date', response.json())

    def test_get_unpaid(self):
        """Test getting list of unpaid timesheets."""
        response = self.client.get('/api/timesheets/unpaid/')
        self.assertEqual(response.status_code, 200, response)
