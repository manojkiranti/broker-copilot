import logging
from rest_framework import serializers
from rest_framework.fields import SerializerMethodField
from django.db.models import Q
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