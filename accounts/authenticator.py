import httpx, os
import requests
import os
from authlib.jose import jwt
from rest_framework.views import APIView
from django.core.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework import status
from enum import Enum

from django.contrib.auth import get_user_model, login
User = get_user_model()

class AllowedDomains(Enum):
    ODIN_MORTGAGE = 'odinmortgage.com'

class GoogleOAuthHandler(APIView):
    permission_classes = (AllowAny, )

    def get_userinfo(self, access_token):
        userinfo_endpoint = 'https://www.googleapis.com/oauth2/v1/userinfo'
        response = requests.get(userinfo_endpoint, headers={
                                'Authorization': f'Bearer {access_token}'})
        response.raise_for_status()
        return response.json()

    def login_or_create_user(self, request, id, email, name):
        
        user = User.objects.filter(oauth_id=id).first()
        if not user:             
            domain = email.split('@')[-1]  # Get the part after '@'
                
            # Check if the domain is the expected one
            allowed_domains = [domain.value for domain in AllowedDomains]
            if domain not in allowed_domains:
                raise ValidationError("Registration is restricted to users with an allowed email domain.")
            user = User.objects.create_user(
                email=email, fullname=name, oauth_type=3, oauth_id=id, is_verified=True)
            user.save()
        login(request, user)
        refresh = RefreshToken.for_user(user)
        return {
            'data': {
                'access_token': str(refresh.access_token),
                'refresh_token': str(refresh),
                'email': user.email,
                'name': user.fullname,
                'is_active': user.is_active,
                'is_admin': user.is_admin,
            }
        }


class MicrosoftTokenValidator:
    def __init__(self):
        self.public_keys = None

    def fetch_keys(self):
        url = 'https://login.microsoftonline.com/common/discovery/v2.0/keys'
        try:
            with httpx.Client() as client:
                response = client.get(url)
                response.raise_for_status()
                self.public_keys = response.json()['keys']
        except httpx.HTTPStatusError as e:
            self.public_keys = []
        except Exception as e:
            self.public_keys = []
            raise RuntimeError(f'Failed to fetch keys: {str(e)}')

    def validate_token(self, token):
        if not token:
            raise ValueError('Authorization token is missing')

        if not self.public_keys:
            try:
                self.fetch_keys()
            except Exception as e:
                raise RuntimeError(f'Failed to fetch keys: {str(e)}')

            if not self.public_keys:
                raise RuntimeError('Unable to fetch public keys')

        try:
            decoded_token = jwt.decode(token, self.public_keys, claims_options={
                'aud': {'essential': True, 'value': '90f18c66-c807-487e-b544-36f30af759be'},
                'iss': {'essential': True, 'value': 'https://login.microsoftonline.com/common/v2.0'}
            })
            return decoded_token
        except Exception as e:
            raise ValueError(f'JWT validation failed: {str(e)}')
        except:
            raise ValueError(
                f'Unexpected error during token validation: {str(e)}')
