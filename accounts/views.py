import os
import requests
from django.views import View
from rest_framework.views import APIView
from rest_framework.response import Response
from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.permissions import AllowAny
from requests_oauthlib import OAuth2Session
from rest_framework_simplejwt.tokens import RefreshToken
from drf_yasg.utils import swagger_auto_schema
from django.contrib.auth import get_user_model, login
from rest_framework.permissions import IsAuthenticated
from django.template.response import TemplateResponse
from .serializers import (
    UserLoginSerializer, 
    GoogleVerifyAccessTokenSerializer, 
    GoogleVerifyCodeForTokenSerializer,
    UserListSerializer,
    UserFeedbackSerializer,
    UserUpdateSerializer
)
from .authenticator import GoogleOAuthHandler
from .models import UserFeedback
User = get_user_model()

class UserListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # Retrieve query parameters for email and broker_role
        email = request.query_params.get('email', None)
        broker_role = request.query_params.get('broker_role', None)
        fullname = request.query_params.get('name', None)

        # Start with all users
        users = User.objects.all()

        # Apply email filter if provided
        if email:
            users = users.filter(email__icontains=email)

        # Apply fullname filter if provided
        if fullname:
            users = users.filter(fullname__icontains=fullname)
        
        # Apply broker_role filter if provided
        if broker_role:
            users = users.filter(broker_role=broker_role)

        # Serialize the filtered queryset
        serializer = UserListSerializer(users, many=True)
        return Response({
            "success": True,
            "data": serializer.data
        },status=status.HTTP_200_OK)
    
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
            'fullname': user.fullname,
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
        print(serializer.errors)
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
                # response.set_cookie(key='jwt_authtoken', value=response_data['access_token'], httponly=True)
                return response
            else:
                return Response({
                    "error": "Failed to obtain access token from Google."
                }, status=status.HTTP_400_BAD_REQUEST)

        except ValidationError as e:
            return Response({
                "error": str(e.message)
            }, status=status.HTTP_403_FORBIDDEN)
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
            # response.set_cookie(key='jwt_authtoken', value=response_data['access_token'], httponly=True)
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

class UserFeedbackCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = UserFeedbackSerializer(data=request.data)
        if serializer.is_valid():
            user_feedback = UserFeedback.objects.create(
                user=request.user,
                message=serializer.validated_data['message']
            )
             # Serialize the newly created UserFeedback instance
            serialized_feedback = UserFeedbackSerializer(user_feedback).data
            
            # Prepare the payload for the AI service
            ai_url = os.getenv('AI_URL')
            url = f'{ai_url}/feedback'
            payload = {
                'username': request.user.email,  # Add the authenticated user's username
                'feedback': serializer.validated_data['message']  # Add the feedback content received from the client
            }

            try:
                # Send a POST request to the AI service with the received data
                response = requests.post(url, json=payload)
                response.raise_for_status()  # Raises an HTTPError for bad responses

                # Get data from the response
                ai_response_data = response.json()

                # Combine the serialized feedback and the AI response data
                combined_response = {
                    'user_feedback': serialized_feedback,
                    'ai_response': ai_response_data
                }

                # Return combined data as JSON
                return Response(combined_response, status=status.HTTP_201_CREATED)
            except requests.exceptions.HTTPError as e:
                # Handle HTTP errors (e.g., response 4XX, 5XX)
                return Response({'error': 'HTTP error occurred', 'details': str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
            except requests.exceptions.RequestException as e:
                # Handle other requests related errors (e.g., connection issues)
                return Response({'error': 'Error connecting to AI service', 'details': str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
            except Exception as e:
                # Handle other errors
                return Response({'error': 'An unexpected error occurred', 'details': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def patch(self, request):
        user = request.user
        serializer = UserUpdateSerializer(data=request.data)
        if serializer.is_valid():
            validated_data = serializer.validated_data
            user.fullname = validated_data.get('fullname', user.fullname)
            user.phone = validated_data.get('phone', user.phone)
            user.broker_role = validated_data.get('broker_role', user.broker_role)
            user.save()
            response_data = {
                    "success": True,
                    "statusCode": status.HTTP_200_OK,
                    "message": "Profile updated successfully"
                }
            return Response(response_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        response_data = {
                "success": True,
                "statusCode": status.HTTP_200_OK,
                "data": {
                    "fullname": user.fullname,
                    "phone": user.phone,
                    "broker_role": user.broker_role,
                    "email": user.email
                }
            }
        return Response(response_data, status=status.HTTP_200_OK)

def my_view(request, template_name="index.html"):
    code = request.GET.get('code')
    return TemplateResponse(request, template_name, {'code': code})

