import logging
from rest_framework import serializers
from rest_framework.fields import SerializerMethodField
from django.contrib.auth import authenticate
from django.db.models import Q
import re
from django.contrib.auth import get_user_model

# from .models import User
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

class UserRegisterSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255, required=True)
    fullname = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    password = serializers.CharField(write_only=True, required=True)
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    broker_role = serializers.ChoiceField(choices=User.BROKER_ROLES, required=False)
    
    def validate_password(self, value):
        # Check the length of the password
        if len(value) < 7:
            raise serializers.ValidationError("Password must be at least 7 characters long.")

        # Check for at least one special character
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", value):
            raise serializers.ValidationError("Password must contain at least one special character.")

        return value
    

class UserListSerializer(serializers.ModelSerializer):
    is_profile_complete = SerializerMethodField()
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'fullname', 'is_active', 'phone', 'broker_role', 'is_profile_complete']
        read_only_fields = fields  
    
    def get_is_profile_complete(self, obj):
        """Method to get the state of the user's profile completion."""
        return obj.is_profile_complete()
        
class UserUpdateSerializer(serializers.Serializer):
    fullname = serializers.CharField(max_length=255, required=False, allow_blank=True)
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    broker_role = serializers.ChoiceField(choices=[
            ('broker', 'Broker'),
            ('processor', 'Processor')
        ], required=False, allow_blank=True)
    
class GoogleVerifyCodeForTokenSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=255)

class GoogleVerifyAccessTokenSerializer(serializers.Serializer):
    token = serializers.CharField(max_length=555)

class UserFeedbackSerializer(serializers.Serializer):
    message = serializers.CharField(max_length=1024)