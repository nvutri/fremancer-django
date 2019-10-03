"""Handle view processing for users pages."""
import json

from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth import authenticate as auth_verify, login as auth_login

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes
from rest_framework.decorators import list_route
from rest_framework import status

from fremancer_users.forms import SignupForm, LoginForm
from fremancer_users.models import UserProfile
from fremancer_users.serializers import UserSerializer, UserProfileSerializer


class UserViewSet(viewsets.ModelViewSet):
    """API endpoint that allows users to be viewed or edited."""
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)

    def list(self, request):
        """Get the user data for logged in user."""
        return self.retrieve(request, request.user.id)

    def retrieve(self, request, pk):
        """Get the user data for logged in user."""
        if not request.user.is_authenticated() or str(pk) != str(request.user.id):
            return Response('Invalid Request', status=400)
        user = get_object_or_404(self.queryset, pk=request.user.id)
        user_data = self.combine_user_profile(user)
        return Response(user_data)

    def combine_user_profile(self, user):
        """Return a combined info of user data and its profile."""
        user_serializer = UserSerializer(user)
        user_data = user_serializer.data
        # Get Profile data to merge with user data.
        user_profile = UserProfile.objects.get(user=user)
        profile_data = UserProfileSerializer(user_profile).data
        profile_data.pop('user')  # Remove user as it already existed.
        # Merge user data and profile data.
        user_data.update(profile_data)
        return user_data

    def create(self, request):
        """Create user according to request."""
        response = dict()
        signup_form = SignupForm(request.POST)
        if signup_form.is_valid():
            user = User(email=signup_form.cleaned_data['email'],
                        username=signup_form.cleaned_data['email'],
                        first_name=signup_form.cleaned_data['first_name'],
                        last_name=signup_form.cleaned_data['last_name'])
            user.set_password(signup_form.cleaned_data['password'])
            user.save()
            user_profile = UserProfile(
                user=user,
                membership=signup_form.cleaned_data['membership'],
            )
            user_profile.save()
            return Response(self.combine_user_profile(user))
        else:
            return Response(data={'error': signup_form.errors}, status=status.HTTP_400_BAD_REQUEST)

    @list_route(methods=['post'])
    def logout(self, request):
        """Handle request to cancel session and log out."""
        auth_logout(request)
        return Response(data={'success': True})

    @list_route(methods=['post'])
    def authenticate(self, request):
        """Handle session login request."""
        user = auth_verify(
            username=request.POST['username'],
            password=request.POST['password']
        )
        if user is None:
            return Response(
                data={
                    'password': 'Please enter a correct username and password. Note that both fields may be case-sensitive.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        else:
            if user.is_active:
                auth_login(request, user)
                user_data = self.combine_user_profile(request.user)
                return Response(data=user_data)
            else:
                return Response(
                    data={'username': 'Username is no longer active'},
                    status=status.HTTP_400_BAD_REQUEST)

    @list_route(methods=['post'])
    def is_authenticated(self, request):
        """Provide session verificatin of already authenticated."""
        if request.user.is_authenticated():
            user_data = self.combine_user_profile(request.user)
            return Response(data={
                'success': True,
                'user': user_data
            })
        return Response(data={'success': False})


class UserProfileViewSet(viewsets.ModelViewSet):
    """API endpoint that allows users to be viewed or edited."""
    queryset = UserProfile.objects.all().order_by('user')
    serializer_class = UserProfileSerializer
    filter_fields = ('membership',)
