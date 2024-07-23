from django.shortcuts import render
import requests
import base64
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views  import APIView
from rest_framework.permissions import IsAuthenticated
import os
# Create your views here.

# Helper function to get encoded headers
def get_encoded_headers():
    DB_USER = os.getenv('WEBSITE_USER')
    DB_PASSWORD = os.getenv('WEBSITE_PASSWORD')
    encoded_credentials = base64.b64encode(f"{DB_USER}:{DB_PASSWORD}".encode()).decode()
    headers = {
        "Authorization": f"Basic {encoded_credentials}"
    }
    return headers

class WebsiteDataListAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk, *args, **kwargs):
        website_url = os.getenv('WEBSITE_URL')
        base_url = f'{website_url}/forms/{pk}/entries?_labels=1'
        
        # Additional parameters
        params = {
            "paging[page_size]": request.query_params.get('page_size', 10),
            "paging[current_page]": request.query_params.get('current_page', 1)
        }
        
        # Check if search parameter is provided
        search_param = request.query_params.get('search')
        if search_param:
            params["search"] = search_param
            
        # Get encoded headers
        headers = get_encoded_headers()
        
        try:
            # Make the GET request
            response = requests.get(base_url, params=params, headers=headers)
            response.raise_for_status()  # Raises an HTTPError for bad responses

            # Return data as JSON
            return Response(response.json(), status=status.HTTP_200_OK)
        except requests.exceptions.HTTPError as e:
            # Handle HTTP errors (e.g., response 4XX, 5XX)
            return Response({'error': 'HTTP error occurred', 'details': str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        except requests.exceptions.RequestException as e:
            # Handle other requests related errors (e.g., connection issues)
            return Response({'error': 'Error connecting to the service', 'details': str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        except Exception as e:
            # Handle other errors
            return Response({'error': 'An unexpected error occurred', 'details': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
  
class WesiteDataDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk, *args, **kwargs):
        website_url = os.getenv('WEBSITE_URL')
        base_url = f'{website_url}/entries/{pk}/?_labels=1'
    
            
         # Get encoded headers
        headers = get_encoded_headers()
        
        try:
            # Make the GET request
            response = requests.get(base_url, headers=headers)
            response.raise_for_status()  # Raises an HTTPError for bad responses

            # Return data as JSON
            return Response(response.json(), status=status.HTTP_200_OK)
        except requests.exceptions.HTTPError as e:
            # Handle HTTP errors (e.g., response 4XX, 5XX)
            return Response({'error': 'HTTP error occurred', 'details': str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        except requests.exceptions.RequestException as e:
            # Handle other requests related errors (e.g., connection issues)
            return Response({'error': 'Error connecting to the service', 'details': str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        except Exception as e:
            # Handle other errors
            return Response({'error': 'An unexpected error occurred', 'details': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)      
        

class WebsiteDataLabelsAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request,  *args, **kwargs):
        website_url = os.getenv('WEBSITE_URL')
        base_url = f'{website_url}/entries?_labels=1'
        
        # Get encoded headers
        headers = get_encoded_headers()
        
        try:
            # Make the GET request
            response = requests.get(base_url, headers=headers)
            response.raise_for_status()  # Raises an HTTPError for bad responses

            # Return data as JSON
            return Response(response.json(), status=status.HTTP_200_OK)
        except requests.exceptions.HTTPError as e:
            # Handle HTTP errors (e.g., response 4XX, 5XX)
            return Response({'error': 'HTTP error occurred', 'details': str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        except requests.exceptions.RequestException as e:
            # Handle other requests related errors (e.g., connection issues)
            return Response({'error': 'Error connecting to the service', 'details': str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        except Exception as e:
            # Handle other errors
            return Response({'error': 'An unexpected error occurred', 'details': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)    