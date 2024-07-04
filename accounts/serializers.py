import logging
logger = logging.getLogger(__name__)
from rest_framework import serializers
from .authenticator import TokenValidator
from django.contrib.auth import get_user_model
User = get_user_model()


class OAuthUserLoginSerializer(serializers.Serializer):
    oauth_type = serializers.IntegerField()
    token = serializers.CharField()

    def validate(self, data):
        oauth_type = data.get('oauth_type')
        token = data.get('token')

        validator = TokenValidator()

        try:
            # Validate and decode token
            decoded_token = validator.validate_token(token)
            email = decoded_token.get('preferred_username')

            # Validate for Microsoft OAuth specific requirements
            if oauth_type != User.OauthType.MICROSOFT:
                logger.error('Invalid Outlook OAuth type')
                raise serializers.ValidationError('Invalid Outlook OAuth type')

            # Check if user already exists based on email
            user = User.objects.filter(email=email).first()

            if user:
                data['user'] = user
            else:
                # Create a new user if not exists
                user = User.objects.create_user(email=email)
                data['user'] = user
            return data

        except ValueError as e:
            logger.error(str(e))
            raise serializers.ValidationError(str(e))
