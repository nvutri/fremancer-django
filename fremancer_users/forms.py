from django import forms as django_forms
from django.contrib.auth.models import User


class SignupForm(django_forms.ModelForm):
    """SignUp Form Validation."""

    class Meta:
        model = User
        fields = ('email', 'password', 'first_name', 'last_name')


    MIN_PASSWORD_LENGTH = 8

    membership = django_forms.CharField(
        min_length=3,
        required=True
    )

    def clean_email(self):
        """Verify email is not duplicated and valid."""
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise django_forms.ValidationError('Email Already Used.')
        return email

    def clean_password(self):
        """Verify a clean password."""
        password = self.cleaned_data['password'].strip()
        if len(password) < self.MIN_PASSWORD_LENGTH:
            raise django_forms.ValidationError('Password must be at least %s characters' % self.MIN_PASSWORD_LENGTH)
        return password


class LoginForm(django_forms.ModelForm):
    """Login Form Validation."""

    class Meta:
        model = User
        fields = ('email', 'password')

    def clean_email(self):
        email = self.cleaned_data['email']
        if not User.objects.filter(email=email).exists():
            raise django_forms.ValidationError('Email does not exists.')
        return email
