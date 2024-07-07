import os
import requests
from django.views import View
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from requests_oauthlib import OAuth2Session
from rest_framework_simplejwt.tokens import RefreshToken
from drf_yasg.utils import swagger_auto_schema
from django.contrib.auth import get_user_model, login
from django.template.response import TemplateResponse
from .serializers import (
    UserLoginSerializer, 
    GoogleVerifyAccessTokenSerializer, 
    GoogleVerifyCodeForTokenSerializer
)
from .authenticator import GoogleOAuthHandler
import logging

logging.basicConfig(level=logging.DEBUG)

User = get_user_model()
class UserLoginView(APIView):
    permission_classes = (AllowAny, )

    @swagger_auto_schema(request_body=UserLoginSerializer, operation_id='1_login', tags=['AUTH'])
    def post(self, request, *args, **kwargs):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        login(request, user)
        refresh = RefreshToken.for_user(user)
        return Response({
            'access_token': str(refresh.access_token),
            'refresh_token': str(refresh),
            'email': user.email,
            'is_active': user.is_active,
            'is_admin': user.is_admin,
        }, status=status.HTTP_200_OK)

class GenerateGoogleSignInLink(APIView):
    permission_classes = (AllowAny, )

    @swagger_auto_schema(operation_id='2_generate_google_signin_link', tags=['AUTH'])
    def get(self, request):
        auth_params = {
            'client_id': os.getenv('GOOGLE_CLIENT_ID'),
            'redirect_uri': os.getenv('REDIRECT_URI'),
            'scope': 'openid profile email',
            'response_type': 'code',
        }
        auth_url = 'https://accounts.google.com/o/oauth2/auth?' + '&'.join(f'{key}={val}' for key, val in auth_params.items())
        return Response({
            "success": True,
            "data": {
                'google_signin_link': auth_url
            }
        }, status=status.HTTP_200_OK)


class GoogleVerifyCodeForToken(GoogleOAuthHandler):

    @swagger_auto_schema(request_body=GoogleVerifyCodeForTokenSerializer, operation_id='3_verify_code_for_token', tags=['AUTH'])
    def post(self, request):
        serializer = GoogleVerifyCodeForTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # import pdb; pdb.set_trace();

        try:
            # Initialize OAuth2Session with client credentials
            oauth = OAuth2Session(os.getenv('GOOGLE_CLIENT_ID'), redirect_uri=os.getenv('REDIRECT_URI'))
            # Fetch token using authorization code
            token = oauth.fetch_token(
                token_url='https://oauth2.googleapis.com/token',
                code=serializer.validated_data['code'],
                client_id=os.getenv('GOOGLE_CLIENT_ID'),
                client_secret=os.getenv('GOOGLE_CLIENT_SECRET')
            )

            # Use the obtained token to fetch user info
            userinfo = oauth.get('https://www.googleapis.com/oauth2/v1/userinfo').json()

            if userinfo:
                response_data = self.login_or_create_user(request, userinfo['id'], userinfo['email'], userinfo.get('name', ''))
                response = Response(response_data, status=status.HTTP_200_OK)
                response.set_cookie(key='jwt_authtoken', value=response_data['access_token'], httponly=True)
                return response
            else:
                return Response({
                    "error": "Failed to obtain access token from Google."
                }, status=status.HTTP_400_BAD_REQUEST)
        except requests.RequestException as e:
            return Response({
                "error": "Failed to obtain token from Google.",
                "details": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                "error": "An unexpected error occurred.",
                "details": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        
class GoogleVerifyAccessToken(GoogleOAuthHandler):

    @swagger_auto_schema(request_body=GoogleVerifyAccessTokenSerializer, operation_id='4_verify_access_token', tags=['AUTH'])
    def post(self, request):
        serializer = GoogleVerifyAccessTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            userinfo = self.get_userinfo(serializer.validated_data['token'])
            response_data = self.login_or_create_user(request, userinfo['id'], userinfo['email'], userinfo.get('name', ''))
            response = Response(response_data, status=status.HTTP_200_OK)
            response.set_cookie(key='jwt_authtoken', value=response_data['access_token'], httponly=True)
            return response
        except requests.RequestException as e:
            return Response({
                "error": "Failed to obtain user information from Google.",
                "details": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                "error": "An unexpected error occurred.",
                "details": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

def my_view(request, template_name="index.html"):
    code = request.GET.get('code')
    return TemplateResponse(request, template_name, {'code': code})
