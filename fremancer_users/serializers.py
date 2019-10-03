from django.contrib.auth.models import User
from fremancer_users.models import UserProfile, UserBank

from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name')


class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = UserProfile
        fields = '__all__'


class UserBankSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserBank
        fields = '__all__'
