from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from .serializers import OAuthUserLoginSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from drf_yasg.utils import swagger_auto_schema
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
