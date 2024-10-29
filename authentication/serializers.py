import logging
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.db.models import Q
import re
from django.contrib.auth import get_user_model

# from .models import User
logger = logging.getLogger(__name__)
User = get_user_model()

class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=255)
    password = serializers.CharField(max_length=255)
    code = serializers.CharField(max_length=6, required=False, write_only=True)
    
    def validate(self, data):
        username = data.get('username')
        password = data.get('password')
        code = data.get('code')

        if not username or not password:
            raise serializers.ValidationError('Please provide username and password.')

        user = User.objects.filter(Q(username=username) | Q(email=username)).first()

        if not user:
            raise serializers.ValidationError('Please provide a valid username or email and password.')

        if user.oauth_type != 0 and user.password is None:
            raise serializers.ValidationError('Please try to login with registered social account.')

        authenticated_user = authenticate(email=user.email, password=password)

        if not authenticated_user:
            raise serializers.ValidationError('Invalid credentials.')

        data['user'] = authenticated_user

        if user.two_factor_enabled:
            if not code:
                data['two_factor_required'] = True
            else:
                import pyotp
                totp = pyotp.TOTP(user.two_factor_secret)
                if not totp.verify(code):
                    raise serializers.ValidationError('Invalid 2FA code.')
        
        return data