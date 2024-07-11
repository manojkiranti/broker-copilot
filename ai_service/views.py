from rest_framework.response import Response
from rest_framework import status
from rest_framework.views  import APIView
from rest_framework.permissions import AllowAny
from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import IsAuthenticated
import requests
import os
from django.shortcuts import render

# Create your views here.

class getAISettings(APIView):
    permission_classes = (AllowAny, )
    @swagger_auto_schema(tags=['AI Service'])
    def get(self, request, *args, **kwargs):
        # Define the API endpoint
        ai_url = os.getenv('AI_URL')
        url = f'{ai_url}/auth_setup'
        
        try:
            # Send a GET request to the API endpoint
            response = requests.get(url)
            response.raise_for_status()  # Raises an HTTPError for bad responses

            # Get data from the response
            data = response.json()

            # Return data as JSON
            return Response(data, status=status.HTTP_200_OK)
        except requests.exceptions.HTTPError as e:
            # Handle HTTP errors (e.g., response 4XX, 5XX)
            return Response({'error': 'HTTP error occurred', 'details': str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        except requests.exceptions.RequestException as e:
            # Handle other requests related errors (e.g., connection issues)
            return Response({'error': 'Error connecting to AI service', 'details': str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        except Exception as e:
            # Handle other errors
            return Response({'error': 'An unexpected error occurred', 'details': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class FeedbackAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        ai_url = os.getenv('AI_URL')
        url = f'{ai_url}/feedback'
        payload = {
            'username': request.user.email,  # Add the authenticated user's username
            'feedback': request.data.get('feedback')  # Add the feedback content received from the client
        }
        try:
            # Send a POST request to the AI service with the received data
            response = requests.post(url, json=payload)
            response.raise_for_status()  # Raises an HTTPError for bad responses

            # Get data from the response
            data = response.json()

            # Return data as JSON
            return Response(data, status=status.HTTP_200_OK)
        except requests.exceptions.HTTPError as e:
            # Handle HTTP errors (e.g., response 4XX, 5XX)
            return Response({'error': 'HTTP error occurred', 'details': str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        except requests.exceptions.RequestException as e:
            # Handle other requests related errors (e.g., connection issues)
            return Response({'error': 'Error connecting to AI service', 'details': str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        except Exception as e:
            # Handle other errors
            return Response({'error': 'An unexpected error occurred', 'details': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    
class getAIAccountInfo(APIView):
    permission_classes = (AllowAny, )
    @swagger_auto_schema(tags=['AI Service'])
    def get(self, request, *args, **kwargs):
        return Response("success", status=status.HTTP_200_OK)