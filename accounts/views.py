import os, requests
from django.views import View
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from .serializers import OAuthUserLoginSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from drf_yasg.utils import swagger_auto_schema
from django.shortcuts import render
from django.contrib.auth import get_user_model, login
User = get_user_model()

class OAuthUserLoginAPIView(APIView):
    permission_classes = [AllowAny]
  
    @swagger_auto_schema(request_body=OAuthUserLoginSerializer, tags=["AUTH"])
    def post(self, request):
        serializer = OAuthUserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        login(request, user)
        refresh = RefreshToken.for_user(user)
        access = str(refresh.access_token)
        response = Response({
            'access_token': access,
            'refresh_token': str(refresh),
            'email': user.email,
            'is_active': user.is_active,
            'is_admin': user.is_admin,
            'status': status.HTTP_200_OK
        }, status=status.HTTP_200_OK)
        response.set_cookie(key='jwt_authtoken', value=access, httponly=True)
        return response
    

class GenerateGoogleSignInLink(APIView):
    def get(self, request):
        auth_params = {
            'client_id': os.getenv('GOOGLE_CLIENT_ID'),
            'redirect_uri': os.getenv('REDIRECT_URI'),
            'scope': 'openid profile email',
            'response_type': 'code',
        }
        auth_url = 'https://accounts.google.com/o/oauth2/auth?' + '&'.join(f'{key}={val}' for key, val in auth_params.items())
        response_data = {
			"success": True,
			"statusCode": status.HTTP_200_OK,
			"data": {
                'google_signin_link': auth_url
            }
		}
        return Response(response_data, status=status.HTTP_200_OK)
    

class GoogleVerifyCodeForToken(APIView):
    def post(self, request):
        try:
            code = request.data.get('code')
            
            token_endpoint = 'https://oauth2.googleapis.com/token'
            data = {
                'code': code,
                'client_id': os.getenv('GOOGLE_CLIENT_ID'),
                'client_secret': os.getenv('GOOGLE_CLIENT_SECRET'),
                'redirect_uri': os.getenv('REDIRECT_URI'),
                'grant_type': 'authorization_code',
            }
            
            token_response = requests.post(token_endpoint, data=data)
            token_data = token_response.json()
            access_token = token_data.get('access_token')

            if access_token:
                userinfo_endpoint = 'https://www.googleapis.com/oauth2/v1/userinfo'
                userinfo_response = requests.get(userinfo_endpoint, headers={'Authorization': f'Bearer {access_token}'})
                userinfo = userinfo_response.json()
                user = User.objects.filter(email=userinfo['email']).first()
                if user:
                    login(request, user)
                    refresh = RefreshToken.for_user(user)
                    access = str(refresh.access_token)
                    response = Response({
                        'access_token': access,
                        'refresh_token': str(refresh),
                        'email': user.email,
                        'is_active': user.is_active,
                        'is_admin': user.is_admin,
                        'status': status.HTTP_200_OK
                    }, status=status.HTTP_200_OK)
                    response.set_cookie(key='jwt_authtoken', value=access, httponly=True)
                    return response
                else:
                    user = User.objects.create_user(email=userinfo['email'], fullname=userinfo.get('fullname', ''))
                    login(request, user)
                    refresh = RefreshToken.for_user(user)
                    access = str(refresh.access_token)
                    response = Response({
                        'access_token': access,
                        'refresh_token': str(refresh),
                        'email': user.email,
                        'is_active': user.is_active,
                        'is_admin': user.is_admin,
                        'status': status.HTTP_200_OK
                    }, status=status.HTTP_200_OK)
                    response.set_cookie(key='jwt_authtoken', value=access, httponly=True)
                    return response
            return Response(
                {
                    "error": {
                        "statusCode": status.HTTP_400_BAD_REQUEST,
                        "message": "Failed to obtain access token.",
                    }
                }, status=status.HTTP_400_BAD_REQUEST
            )

        except Exception as e:
            return Response(
                {
                    "error": {
                        "statusCode": status.HTTP_400_BAD_REQUEST,
                        "message": f"Something went wrong. Please try again! Error: {e}",
                    }
                }, status=status.HTTP_400_BAD_REQUEST
            )

    

from django.template.response import TemplateResponse
def my_view(request, template_name="index.html"):
    code = request.GET.get('code')
    print(code)
    args = {}
    args['code'] = code
    return TemplateResponse(request, template_name, args)
