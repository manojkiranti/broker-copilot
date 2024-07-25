from django.shortcuts import render
import requests
import base64
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views  import APIView
from rest_framework.permissions import IsAuthenticated
from opportunity_app.models import ContactsOpportunity
import os
import re
import datetime
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

class WebsiteCreateLatestContactAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def validate_email(self, email):
        # Basic email validation pattern
        pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        return re.match(pattern, email) is not None
    
    
    def post(self, request, *args, **kwargs):
        from_id = request.data.get('from_id', 8)
        website_url = os.getenv('WEBSITE_URL')
        base_url = f'{website_url}/forms/{from_id}/entries'
       
        # Additional parameters
        # Conditionally add pagination parameters
        page_size = request.data.get('page_size', 20)
        page_number = request.data.get('page_number', 1)
        params = {
                "paging[page_size]": page_size,
                "paging[current_page]": page_number
            }
        
        # Get encoded headers
        headers = get_encoded_headers()
        try:
                # Make the GET request
                response = requests.get(base_url,params=params, headers=headers)
                response.raise_for_status()  # Raises an HTTPError for bad responses
                # Parse response data
                data = response.json()
                entries = data.get('entries', [])
                # Process each entry in the 'entries' list
                
                if entries:
                    for entry in entries:

                        # Create and save new Contact instance
                        email = entry.get('192')
                        date_str = entry.get('date_updated')
                        
                        # Parse the datetime string
                        date_updated = datetime.datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S') if date_str else None
                        phone = entry.get('193', '').strip()
                        if phone:
                            phone = phone[:24]
                        # Validate email
                        if email and self.validate_email(email):
                            # Prepare the payload, setting None for any empty values
                            name_part1 = entry.get('186', '').strip()
                            name_part2 = entry.get('188', '').strip()
                            # Determine the name based on the availability of parts
                            if name_part1 or name_part2:
                                name = f"{name_part1} {name_part2}".strip()
                            else:
                                name = None
                            payload = {
                                'name': name,
                                'email': email,
                                'phone': phone or None,
                                'residency': entry.get('46.6', None) if entry.get('46.6', '').strip() else None,
                                'website_field_id': entry.get('id'),
                                'website_form_id': entry.get('form_id'),
                                'website_date_updated': date_updated,
                            }
        
                            
                            # Create and save new Contact instance
                            # Update existing or create new record
                            contact, created = ContactsOpportunity.objects.update_or_create(
                                email=email,  # Look up by email
                                defaults=payload  # Update these fields or create new entry with these
                            )
                return Response(data, status=status.HTTP_200_OK)
        except requests.exceptions.HTTPError as e:
                # Handle HTTP errors (e.g., response 4XX, 5XX)
                return Response({'error': 'HTTP error occurred', 'details': str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        except requests.exceptions.RequestException as e:
            # Handle other requests related errors (e.g., connection issues)
            return Response({'error': 'Error connecting to the service', 'details': str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        except Exception as e:
            # Handle other errors
                return Response({'error': 'An unexpected error occurred', 'details': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)    
            
          
                             
class WebisteCreateContactAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def validate_email(self, email):
        # Basic email validation pattern
        pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        return re.match(pattern, email) is not None
    
    def email_exists(self, email):
        # Check if an email already exists in the database
        return ContactsOpportunity.objects.filter(email=email).exists()
    



    def post(self, request, *args, **kwargs):
        from_id = request.data.get('from_id', 8)
        website_url = os.getenv('WEBSITE_URL')
        base_url = f'{website_url}/forms/{from_id}/entries'
       
        # Additional parameters
        # Conditionally add pagination parameters
        page_size = request.data.get('page_size', 100)
        page_number = request.data.get('page_number', 1)
            
        # Get encoded headers
        headers = get_encoded_headers()
        entries_exist = True
        
        while entries_exist:
            params = {
                "paging[page_size]": page_size,
                "paging[current_page]": page_number
            }
            try:
                # Make the GET request
                response = requests.get(base_url,params=params, headers=headers)
                response.raise_for_status()  # Raises an HTTPError for bad responses
                # Parse response data
                data = response.json()
                entries = data.get('entries', [])
                # Process each entry in the 'entries' list
                
                if entries:
                    for entry in entries:

                        # Create and save new Contact instance
                        email = entry.get('192')
                        date_str = entry.get('date_updated')
                        
                        # Parse the datetime string
                        date_updated = datetime.datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S') if date_str else None
                        phone = entry.get('193', '').strip()
                        if phone:
                            phone = phone[:24]
                        # Validate email
                        if email and self.validate_email(email) and not self.email_exists(email):
                            # Prepare the payload, setting None for any empty values
                            name_part1 = entry.get('186', '').strip()
                            name_part2 = entry.get('188', '').strip()
                            # Determine the name based on the availability of parts
                            if name_part1 or name_part2:
                                name = f"{name_part1} {name_part2}".strip()
                            else:
                                name = None
                            payload = {
                                'name': name,
                                'email': email,
                                'phone': phone or None,
                                'residency': entry.get('46.6', None) if entry.get('46.6', '').strip() else None,
                                'website_field_id': entry.get('id'),
                                'website_form_id': entry.get('form_id'),
                                'website_date_updated': date_updated,
                            }
        
                            
                            # Create and save new Contact instance
                            ContactsOpportunity.objects.create(**payload)
                    
                    page_number += 1
                else:
                    # Stop the loop if no entries
                    entries_exist = False   
                        
            except requests.exceptions.HTTPError as e:
                # Handle HTTP errors (e.g., response 4XX, 5XX)
                return Response({'error': 'HTTP error occurred', 'details': str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
            except requests.exceptions.RequestException as e:
                # Handle other requests related errors (e.g., connection issues)
                return Response({'error': 'Error connecting to the service', 'details': str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
            except Exception as e:
                # Handle other errors
                return Response({'error': 'An unexpected error occurred', 'details': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        # Return a successful response at the end of the data fetch
        return Response({'message': 'Data fetched and processed successfully'}, status=status.HTTP_200_OK)