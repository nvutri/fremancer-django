from django.contrib.auth.models import User
from django.core.validators import EmailValidator, MaxValueValidator, MinValueValidator, MinLengthValidator, RegexValidator
from django.db import models

DIGITS_ONLY_REGEX = RegexValidator('\d+')


class FremancerWithdrawal(models.Model):
    """A model for freelancer to withdraw money."""
    MAX_INVOICE_AMOUNT = 5000  # One thousand USD.
    MIN_INVOICE_AMOUNT = 5  # 5 USD.

    freelancer = models.ForeignKey(User, related_name='withdrawal_freelancer')
    receive = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[
            MaxValueValidator(MAX_INVOICE_AMOUNT),
            MinValueValidator(MIN_INVOICE_AMOUNT)
        ],
        blank=True, null=True)
    fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True, null=True)
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[
            MaxValueValidator(MAX_INVOICE_AMOUNT),
            MinValueValidator(MIN_INVOICE_AMOUNT)
        ])
    method = models.CharField(max_length=25, choices=[
        ['wu', 'Western Union'],
        ['moneygram', 'Money Gram'],
        ['paypal', 'PayPal'],
        ['payoneer', 'Payoneer']
    ])
    receive_method = models.CharField(max_length=25, choices=[
        ['cash', 'Cash at Location'],
        ['bank', 'Bank Account']
    ])
    status = models.CharField(max_length=25, default='submitted', choices=[
        ['submitted', 'Submitted'],
        ['processed', 'Processed'],
        ['finished', 'Finished'],
        ['cancelled', 'Cancelled']
    ])
    cancel = models.BooleanField(default=False, blank=True)

    first_name = models.CharField(max_length=255, validators=[MinLengthValidator(2)])
    last_name = models.CharField(max_length=255, validators=[MinLengthValidator(2)])
    email = models.CharField(max_length=255, validators=[EmailValidator])
    phone_number = models.CharField(max_length=255, blank=True, null=True, validators=[MinLengthValidator(5)])
    country = models.CharField(max_length=255)
    region = models.CharField(max_length=255)

    bank_number = models.CharField(max_length=255, blank=True, null=True, validators=[DIGITS_ONLY_REGEX])
    bank_iban = models.CharField(max_length=255, blank=True, null=True, validators=[DIGITS_ONLY_REGEX])
    bank_swift = models.CharField(max_length=255, blank=True, null=True, validators=[DIGITS_ONLY_REGEX])

    date_created = models.DateTimeField(auto_now_add=True)
    date_changed = models.DateTimeField(auto_now=True)
