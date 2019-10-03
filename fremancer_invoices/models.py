from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from fremancer_timesheets.models import FremancerTimeSheet
from fremancer_contracts.models import FremancerContract


class FremancerInvoice(models.Model):
    """An invoice for freelancer and hirer."""
    MAX_INVOICE_AMOUNT = 10000  # Ten thousand USD.
    MIN_INVOICE_AMOUNT = 5  # 5 USD.

    hirer = models.ForeignKey(
        User,
        related_name='invoice_hirer')
    freelancer = models.ForeignKey(
        User,
        blank=True,
        null=True,
        related_name='invoice_freelancer')
    contract = models.ForeignKey(
        FremancerContract,
        related_name='invoice_contract')
    timesheets = models.ManyToManyField(
        FremancerTimeSheet,
        related_name='fremancer_invoice')
    paid = models.BooleanField(default=False)
    total_hours = models.DecimalField(
        default=0.0,
        max_digits=7,
        decimal_places=2)
    fee = models.DecimalField(
        default=0.0,
        max_digits=10,
        decimal_places=2,
        validators=[
            MaxValueValidator(MAX_INVOICE_AMOUNT),
            MinValueValidator(MIN_INVOICE_AMOUNT)
        ])
    amount = models.DecimalField(
        default=0.0,
        max_digits=10,
        decimal_places=2,
        validators=[
            MaxValueValidator(MAX_INVOICE_AMOUNT),
            MinValueValidator(MIN_INVOICE_AMOUNT)
        ])
    total_amount = models.DecimalField(
        default=0.0,
        max_digits=10,
        decimal_places=2,
        validators=[
            MaxValueValidator(MAX_INVOICE_AMOUNT),
            MinValueValidator(MIN_INVOICE_AMOUNT)
        ])

    stripe_charge_id = models.CharField(max_length=100, blank=True, null=True)
    stripe_charge_status = models.CharField(max_length=100, blank=True, null=True)

    date_created = models.DateTimeField(auto_now_add=True)
    date_changed = models.DateTimeField(auto_now=True)

    @property
    def status(self):
        if self.stripe_charge_status:
            charge_status = '%s Payment' % self.stripe_charge_status
            return charge_status.title()
        return 'Invoiced'

    @property
    def pending(self):
        return self.stripe_charge_status == 'pending'

    @property
    def contract_data(self):
        return self.contract

    @property
    def timesheets_data(self):
        return self.timesheets
