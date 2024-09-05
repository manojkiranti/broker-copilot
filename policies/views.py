from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import BankPolicy
from .serializers import BankPolicySerializer

# Create your views here.

class BankPolicyListAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        bank_policies = BankPolicy.objects.all()
        serializer = BankPolicySerializer(bank_policies, many=True)
        response_data = {
                "success": True,
                "statusCode": status.HTTP_200_OK,
                "data": serializer.data,
            }
        return Response(response_data, status=status.HTTP_200_OK)
    
    