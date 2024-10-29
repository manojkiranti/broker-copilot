import os
import requests

import pyotp
import qrcode
import base64
from io import BytesIO
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from drf_yasg.utils import swagger_auto_schema
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated

from .serializers import (
    UserLoginSerializer,
)

User = get_user_model()

class TwoFactorVerifyView(APIView):
    permission_classes = (AllowAny, )  # Temporarily allow any since we're verifying tokens

    def post(self, request, *args, **kwargs):
        temp_token = request.data.get('temp_token')
        code = request.data.get('code')

        if not temp_token or not code:
            return Response({'error': 'Temp token and 2FA code are required.'}, status=status.HTTP_400_BAD_REQUEST)

        # Decode and verify the temp_token
        from rest_framework_simplejwt.tokens import AccessToken
        try:
            token = AccessToken(temp_token)
            if not token.payload.get('two_factor'):
                return Response({'error': 'Invalid temp token.'}, status=status.HTTP_400_BAD_REQUEST)
            user_id = token.payload.get('user_id')
            user = User.objects.get(id=user_id)
        except (TokenError, User.DoesNotExist):
            return Response({'error': 'Invalid or expired temp token.'}, status=status.HTTP_400_BAD_REQUEST)

        # Verify the 2FA code
        totp = pyotp.TOTP(user.two_factor_secret)
        if not totp.verify(code):
            return Response({'error': 'Invalid 2FA code.'}, status=status.HTTP_400_BAD_REQUEST)

        # 2FA is valid, issue the actual tokens
        refresh = RefreshToken.for_user(user)
        return Response({
            'access_token': str(refresh.access_token),
            'refresh_token': str(refresh),
            'fullname': user.fullname,
            'email': user.email,
            'is_active': user.is_active,
            'is_admin': user.is_admin,
            'is_2fa_enabled': user.two_factor_enabled,
            'two_factor_required': False
        }, status=status.HTTP_200_OK)
        
class EnableTwoFactorView(APIView):
    permission_classes = (IsAuthenticated, )

    def post(self, request, *args, **kwargs):
        user = request.user
        if user.two_factor_enabled:
            return Response({'error': '2FA is already enabled.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Generate a secret key
        import pyotp
        import qrcode
        import base64
        from io import BytesIO

        secret = pyotp.random_base32()
        user.two_factor_secret = secret
        user.save()

        # Generate provisioning URI
        otp_uri = pyotp.totp.TOTP(secret).provisioning_uri(name=user.email, issuer_name="brokercopilot")

        # Generate QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(otp_uri)
        qr.make(fit=True)
        img = qr.make_image(fill='black', back_color='white')
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        response_data = {
            "success": True,
            "statusCode": status.HTTP_200_OK,
            "data": {'qr_code': img_str, 'secret': secret}
        }
    
        return Response(response_data, status=status.HTTP_200_OK)
    
 
class VerifyTwoFactorView(APIView):
    permission_classes = (IsAuthenticated, )

    def post(self, request, *args, **kwargs):
        user = request.user
        code = request.data.get('code')

        if not user.two_factor_secret:
            return Response({'error': '2FA is not enabled.'}, status=status.HTTP_400_BAD_REQUEST)

        if not code:
            return Response({'error': '2FA code is required.'}, status=status.HTTP_400_BAD_REQUEST)

        totp = pyotp.TOTP(user.two_factor_secret)
        if totp.verify(code):
            user.two_factor_enabled = True
            user.save()
            response_data = {
                "success": True,
                "statusCode": status.HTTP_200_OK,
                "data": {'message': '2FA has been enabled successfully.'}
         }
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            return Response({"error": 'Invalid 2FA code.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)  
           
class DisableTwoFactorView(APIView):
    permission_classes = (IsAuthenticated, )

    def post(self, request, *args, **kwargs):
        user = request.user
        code = request.data.get('code')

        if not user.two_factor_enabled:
            return Response({'detail': '2FA is not enabled.'}, status=status.HTTP_400_BAD_REQUEST)

        if not code:
            return Response({'detail': '2FA code is required to disable.'}, status=status.HTTP_400_BAD_REQUEST)

        totp = pyotp.TOTP(user.two_factor_secret)
        if totp.verify(code):
            user.two_factor_enabled = False
            user.two_factor_secret = ''
            user.save()
            return Response({'detail': '2FA has been disabled successfully.'}, status=status.HTTP_200_OK)
        else:
            return Response({'detail': 'Invalid 2FA code.'}, status=status.HTTP_400_BAD_REQUEST)
    
class UserLoginView(APIView):
    permission_classes = (AllowAny, )

    @swagger_auto_schema(request_body=UserLoginSerializer, operation_id='1_login', tags=['AUTH'])
    def post(self, request, *args, **kwargs):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        
        if user.two_factor_enabled:
            # If 2FA is enabled and code not provided, indicate that 2FA is required
            if not serializer.validated_data.get('two_factor_required', False):
                # Generate and return tokens since 2FA code was provided and verified
                refresh = RefreshToken.for_user(user)
                return Response({
                    'access_token': str(refresh.access_token),
                    'refresh_token': str(refresh),
                    'fullname': user.fullname,
                    'email': user.email,
                    'is_active': user.is_active,
                    'is_admin': user.is_admin,
                    'is_2fa_enabled': user.two_factor_enabled,
                    'two_factor_required': False
                   
                }, status=status.HTTP_200_OK)
            else:
                # 2FA is required, but code not provided yet
                # Generate a temporary token or use a different mechanism
                # Here, we'll use the built-in Simple JWT to issue a temporary token with limited scope

                from rest_framework_simplejwt.tokens import Token
                # Create a unique identifier for 2FA session, could be JWT with a specific claim
                temp_token = RefreshToken()
                temp_token['user_id'] = user.id
                temp_token['two_factor'] = True  # Custom claim to indicate 2FA is pending
                # Set a short expiration time for temp_token
                temp_token.set_exp(lifetime=settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'])

                return Response({
                    'two_factor_required': True,
                    'temp_token': str(temp_token.access_token),
                }, status=status.HTTP_200_OK)
        else:
            # 2FA not enabled, proceed as normal
            refresh = RefreshToken.for_user(user)
            return Response({
                'access_token': str(refresh.access_token),
                'refresh_token': str(refresh),
                'fullname': user.fullname,
                'email': user.email,
                'is_active': user.is_active,
                'is_admin': user.is_admin,
                'is_2fa_enabled': user.two_factor_enabled
            }, status=status.HTTP_200_OK)
            
        # login(request, user)
        # refresh = RefreshToken.for_user(user)
        # return Response({
        #     'access_token': str(refresh.access_token),
        #     'refresh_token': str(refresh),
        #     'fullname': user.fullname,
        #     'email': user.email,
        #     'is_active': user.is_active,
        #     'is_admin': user.is_admin,
        # }, status=status.HTTP_200_OK)