import logging
from rest_framework import serializers
from django.db.models import Q
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)
User = get_user_model()

def authenticate_user(email=None, password=None):
    try:
        user = User.objects.get(email=email)
        if user.check_password(password):
            return user
    except User.DoesNotExist:
        logger.error(f"User with email {email} does not exist.")
    return None

class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=255)
    password = serializers.CharField(max_length=255)

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            raise serializers.ValidationError('Please provide email and password')

        user = User.objects.filter(Q(username=username) | Q(email=username)).first()

        if not user:
            raise serializers.ValidationError('Please provide correct username or email address')

        if user.oauth_type != 0 and user.password is None:
            raise serializers.ValidationError('Please try to login with registered social account')

        authenticated_user = authenticate_user(email=user.email, password=password)

        if not authenticated_user:
            raise serializers.ValidationError('The email and password is not registered')

        data['user'] = authenticated_user
        return data

class GoogleVerifyCodeForTokenSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=255)

class GoogleVerifyAccessTokenSerializer(serializers.Serializer):
    token = serializers.CharField(max_length=555)
