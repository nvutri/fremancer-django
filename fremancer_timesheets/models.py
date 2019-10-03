from django.contrib.auth.models import User
from django.core.exceptions import ValidationError, SuspiciousOperation
from django.db import models

from fremancer_contracts.models import FremancerContract


def validate_monday(day):
    """Validate Monday start date."""
    MONDAY_WEEKDAY = 0
    if day.weekday() != MONDAY_WEEKDAY:
        raise ValidationError(
            'Date %(value)s is not a Monday',
            params={'value': day},
        )


class FremancerTimeSheet(models.Model):
    """A weekly time report for freelancer."""
    contract = models.ForeignKey(FremancerContract)
    user = models.ForeignKey(User)
    start_date = models.DateField(
        validators=[validate_monday])  # Must be a Monday.
    summary = models.TextField(blank=True)
    total_hours = models.DecimalField(
        default=0.0,
        max_digits=7,
        decimal_places=2)
    total_amount = models.DecimalField(
        default=0.0,
        max_digits=10,
        decimal_places=2)

    date_created = models.DateTimeField(auto_now_add=True)
    date_changed = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (('contract', 'start_date'),)
        ordering = ['-start_date']

    def __str__(self):
        return '%s.  %s hours = $%s: %s' % (
            self.id,
            self.total_hours,
            self.total_amount,
            self.summary
        )

    def contract_title(self):
        return self.contract.title

    def invoiced(self):
        return FremancerTimeSheet.objects.filter(pk=self.pk, fremancer_invoice__isnull=False).exists()

    def paid(self):
        return FremancerTimeSheet.objects.filter(pk=self.pk, fremancer_invoice__paid=True).exists()

    def status(self):
        if self.paid():
            return 'Paid'
        elif self.invoiced():
            return 'Invoiced'
        return 'In Progress'

    def is_editable(self):
        """Flag whether a timesheet is editable any more."""
        return False if self.invoiced() or self.paid() else True

    def save(self, *args, **kwargs):
        if self.is_editable():
            super(FremancerTimeSheet, self).save(*args, **kwargs)
        else:
            raise SuspiciousOperation('Timesheet nolonger editable.')


class FremancerDailySheet(models.Model):
    """A daily time report for freelancer."""
    report_date = models.DateField()
    user = models.ForeignKey(User)
    summary = models.TextField(blank=True, null=True)
    hours = models.DecimalField(
        default=0.0,
        max_digits=4,
        decimal_places=2,
        blank=True,
        null=True)
    timesheet = models.ForeignKey(FremancerTimeSheet)

    date_created = models.DateTimeField(auto_now_add=True)
    date_changed = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (('timesheet', 'report_date'),)
        ordering = ['report_date']
