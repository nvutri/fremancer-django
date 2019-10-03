from django.core.validators import RegexValidator
from django.contrib.auth.models import User

from django.db import models
from localflavor.us import models as us_models

DIGITS_ONLY_REGEX = RegexValidator('\d+')


class UserProfile(models.Model):
    """Profile for a regular user."""
    user = models.OneToOneField(User, primary_key=True)
    date_of_birth = models.DateField(verbose_name='Date of Birth', blank=True, null=True)
    profile_picture = models.URLField(max_length=1000, blank=True, null=True)

    phone = us_models.PhoneNumberField(verbose_name='Phone', blank=True, null=True)
    country = models.CharField(max_length=255, blank=True, null=True)
    region = models.CharField(max_length=255, blank=True, null=True)

    # Membership Subscription integrated with Stripe.
    membership = models.CharField(max_length=25, choices=[
        ['freelancer', 'freelancer'],
        ['hirer', 'hirer']
    ])

    def is_freelancer(self):
        return self.membership == 'freelancer'

    def is_hirer(self):
        return self.membership == 'hirer'


class UserBank(models.Model):
    """Banking related information of a user."""
    user = models.OneToOneField(User, primary_key=True)
    # Amount of money exisiting in bank.
    balance = models.DecimalField(
        default=0.0,
        max_digits=10,
        decimal_places=2)
    available = models.DecimalField(
        default=0.0,
        max_digits=10,
        decimal_places=2)
    number = models.CharField(max_length=255, blank=True, null=True, validators=[DIGITS_ONLY_REGEX])
    iban = models.CharField(max_length=255, blank=True, null=True, validators=[DIGITS_ONLY_REGEX])
    swift = models.CharField(max_length=255, blank=True, null=True, validators=[DIGITS_ONLY_REGEX])
    stripe_customer_id = models.CharField(max_length=100, blank=True, null=True)
