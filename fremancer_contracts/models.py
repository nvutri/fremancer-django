from django.contrib.auth.models import User

from django.db import models


class FremancerContract(models.Model):
    """A contract for freelancer and hirer."""
    hirer = models.ForeignKey(User,
        related_name='contract_hirer')
    freelancer = models.ForeignKey(User, blank=True, null=True,
        related_name='contract_freelancer')
    default_payment = models.CharField(
        help_text='Stripe Default Payment ID',
        max_length=100)
    title = models.CharField(max_length=255)
    description = models.TextField()
    total_budget = models.PositiveIntegerField(blank=True, null=True)
    duration = models.CharField(max_length=25, choices=[
        ['short', 'Short Term'],
        ['long', 'Long Term']
    ])
    contract_type = models.CharField(max_length=25, choices=[
        ['hourly', 'Hourly'],
        ['fixed', 'Fixed'],
        ['wage', 'Wage']
    ])

    hourly_rate = models.DecimalField(max_digits=7, decimal_places=2, blank=True, null=True)
    max_weekly_hours = models.PositiveIntegerField(default=40, blank=True, null=True)
    fixed_amount = models.DecimalField(max_digits=7, decimal_places=2, blank=True, null=True)
    wage_amount = models.DecimalField(max_digits=7, decimal_places=2, blank=True, null=True)

    application_type = models.CharField(max_length=25, choices=[
        ['invitation', 'Invitation Only'],
        ['public', 'Public Bidding']
    ], default='invitation')
    accepted = models.BooleanField(default=False, blank=True)

    date_created = models.DateTimeField(auto_now_add=True)
    date_changed = models.DateTimeField(auto_now=True)

    def freelancer_name(self):
        return self.freelancer.get_full_name() if self.freelancer else ''

    def hirer_name(self):
        return self.hirer.get_full_name() if self.hirer else ''

    def is_hourly(self):
        return self.contract_type == 'hourly'

    def is_wage(self):
        return self.contract_type == 'wage'
