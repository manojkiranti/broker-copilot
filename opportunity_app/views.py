from rest_framework.response import Response
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db.models import Q
from rest_framework import status
from rest_framework.views  import APIView
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .serializers import OpportunitySerializer, ContactSerializer
from .models import Opportunity, ContactsOpportunity
from django.contrib.auth import get_user_model

User = get_user_model()

class OpportunityListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get_object(self, pk):
        try:
            return Opportunity.objects.get(pk=pk)
        except Opportunity.DoesNotExist:
            return None
    def get(self, request, *args, **kwargs):
        search_query = request.query_params.get('name', '')
        
        try:
            base_query = Opportunity.objects.filter(
                created_by=request.user, 
                status='active'
            )
            # Filter OpportunityService objects by search query if provided
            if search_query:
                # Using `Q` to add flexibility for possibly more complex search conditions in the future.
                opportunity_services = base_query.filter(
                    Q(name__icontains=search_query)
                )
            else:
                opportunity_services = base_query
            serializer = OpportunitySerializer(
                opportunity_services, many=True)
            response_data = {
                "success": True,
                "statusCode": status.HTTP_200_OK,
                "data": serializer.data,
            }
            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def post(self, request, *args, **kwargs):
        
        serializer = OpportunitySerializer(data=request.data)
       
        serializer.is_valid(raise_exception=True)
        name = serializer.validated_data.get('name')
        if Opportunity.objects.filter(name=name).exists():
            return Response({
                "error": "An opportunity with this name already exists."
            }, status=status.HTTP_400_BAD_REQUEST)
        
        website_tracking_id = serializer.validated_data.get('website_tracking_id')
        
        # Check if website_tracking_id already exists
        if website_tracking_id and Opportunity.objects.filter(website_tracking_id=website_tracking_id).exists():
            return Response({
                "error": "An opportunity with this website tracking ID already exists."
            }, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            opportunity_data = {
                'created_by': request.user,
                'name': serializer.validated_data['name'],
                'type': serializer.validated_data['type'],
                'website_tracking_id': serializer.validated_data.get('website_tracking_id'),
                'json_data': serializer.validated_data.get('json_data', {}),
                'api_request': serializer.validated_data.get('api_request', {}),
                'api_response': serializer.validated_data.get('api_response', {})
            }
            
             # Handling optional primary_contact
            primary_contact = serializer.validated_data.get('primary_contact')
            if primary_contact:
                primary_contact = User.objects.filter(email=primary_contact).first()
                if primary_contact:
                    opportunity_data['primary_contact'] = primary_contact

            # Handling optional secondary_contact
            secondary_contact = serializer.validated_data.get('secondary_contact')
            if secondary_contact:
                secondary_contact = User.objects.filter(email=secondary_contact).first()
                if secondary_contact:
                    opportunity_data['secondary_contact'] = secondary_contact
                    
            
                
            # Check if any user contact info fields are present in the serializer data
            # Handling ContactsOpportunity relationship if provided
            if 'user_contact_email' in serializer.validated_data:
                email = serializer.validated_data['user_contact_email']
                contact, created = ContactsOpportunity.objects.get_or_create(email=email)
                if not created:
                    # Update existing contact (except for the email)
                    contact.name = serializer.validated_data.get('user_contact_name', contact.name)
                    contact.phone = serializer.validated_data.get('user_contact_phone', contact.phone)
                    contact.residency = serializer.validated_data.get('user_contact_residency', contact.residency)
                    contact.updated_by = request.user
                    contact.save()  # Save the updates to the existing contact
                else:
                    # Set additional fields for a newly created contact
                    contact.name = serializer.validated_data.get('user_contact_name')
                    contact.phone = serializer.validated_data.get('user_contact_phone')
                    contact.residency = serializer.validated_data.get('user_contact_residency')
                    contact.created_by = request.user
                    contact.save()  # Save the new contact details

                opportunity_data['user_contact'] = contact

            # Create OpportunityServiceHistory object
            opportunity_service_history = Opportunity.objects.create(**opportunity_data)


            # Prepare response data including ContactInfo details if created
            response_data = {
                "success": True,
                "statusCode": status.HTTP_201_CREATED,
                "data": {
                    "id": opportunity_service_history.id,
                    "name": opportunity_service_history.name.lower(),
                    "api_request": opportunity_service_history.api_request,
                    "api_response": opportunity_service_history.api_response,
                    "status": opportunity_service_history.status,
                    "start_date": opportunity_service_history.start_date,
                    "json_data": opportunity_service_history.json_data,
                    "user_contact": ContactSerializer(opportunity_service_history.user_contact).data
                }
            }

            return Response(response_data, status=status.HTTP_201_CREATED)

        except Exception as e:
            print(e)
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
class AllOpportunityServiceListAPIView(APIView):
    permission_classes = [IsAuthenticated]  # Ensures authorized user can access this view

    def get(self, request, *args, **kwargs):
        opportunity_services = Opportunity.objects.filter(status='active')
        search_query = request.query_params.get('name', '')
        if search_query:
            opportunity_services = opportunity_services.filter(name__icontains=search_query)

        serializer = OpportunitySerializer(opportunity_services, many=True)
        return Response({
            "success": True,
            "statusCode": status.HTTP_200_OK,
            "data": serializer.data,
        }, status=status.HTTP_200_OK)
        


        
class OpportunityServiceDetailUpdateDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get_object(self, pk):
        try:
            return Opportunity.objects.get(pk=pk)
        except Opportunity.DoesNotExist:
            return None
        
    def get(self, request, pk, *args, **kwargs):
        try:
            opportunity_service_history = Opportunity.objects.get(pk=pk, status='active')
            serializer = OpportunitySerializer(opportunity_service_history)
            response_data = {
                "success": True,
                "statusCode": status.HTTP_200_OK,
                "data": serializer.data,
            }
            return Response(response_data, status=status.HTTP_200_OK)
        except Opportunity.DoesNotExist:
            return Response({"error": "Opportunity service history not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def delete(self, request, pk, *args, **kwargs):
        opportunity_service = Opportunity.objects.get( pk=pk)
        if not opportunity_service:
            return Response({"error": "Service not found."}, status=status.HTTP_404_NOT_FOUND)
        
        if request.user != opportunity_service.created_by and \
             request.user != opportunity_service.primary_contact and \
             request.user != opportunity_service.secondary_contact:
            return Response({"error": "You don't have permission to delete this Deals."}, status=status.HTTP_403_FORBIDDEN)
        
        try:
            # Set status to 'inactive' to soft delete the service
            opportunity_service.status = 'inactive'
            opportunity_service.save()
        except (ValidationError, IntegrityError) as e:
            # Handle specific database errors
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            "success": True,
            "statusCode": status.HTTP_200_OK,
            "message": "Successfully deleted deal"
        }, status=status.HTTP_200_OK)

    # Update Opportunity
    def patch(self, request, pk, *args, **kwargs):
        opportunity_service = self.get_object(pk)
        if not opportunity_service:
            return Response({"error": "Deals not found."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = OpportunitySerializer(data=request.data)
       
        serializer.is_valid(raise_exception=True)
        if request.user != opportunity_service.created_by and \
             request.user != opportunity_service.primary_contact and \
             request.user != opportunity_service.secondary_contact:
            return Response({"error": "You don't have permission to update this Deals."}, status=status.HTTP_403_FORBIDDEN)
        
        name = serializer.validated_data.get('name')
        if Opportunity.objects.filter(name=name).exclude(pk=opportunity_service.pk).exists():
            return Response({"error": "An Deal with this name already exists."}, status=status.HTTP_400_BAD_REQUEST)
            
        website_tracking_id = serializer.validated_data.get('website_tracking_id')
        
        
        # Check for website_tracking_id uniqueness except for the current instance
        website_tracking_id = serializer.validated_data.get('website_tracking_id')
        if website_tracking_id:
            if Opportunity.objects.filter(website_tracking_id=website_tracking_id).exclude(pk=pk).exists():
                return Response({
                    "error": "An Deals with this website tracking ID already exists."
                }, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            
            opportunity_service.name = serializer.validated_data.get('name')
            opportunity_service.type = serializer.validated_data.get('type')
            opportunity_service.website_tracking_id = serializer.validated_data.get('website_tracking_id')
            opportunity_service.json_data = serializer.validated_data.get('json_data', {})
            opportunity_service.api_request = serializer.validated_data.get('api_request', {})
            opportunity_service.api_response = serializer.validated_data.get('api_response', {})
             # Handling optional primary_contact
            primary_contact = serializer.validated_data.get('primary_contact')
            if primary_contact:
                primary_contact = User.objects.filter(email=primary_contact).first()
                if primary_contact:
                    opportunity_service.primary_contact = primary_contact

            # Handling optional secondary_contact
            secondary_contact = serializer.validated_data.get('secondary_contact')
            if secondary_contact:
                secondary_contact = User.objects.filter(email=secondary_contact).first()
                if secondary_contact:
                    opportunity_service.secondary_contact = secondary_contact
                    
            
                
            # Check if any user contact info fields are present in the serializer data
            # Handling ContactsOpportunity relationship if provided
            if 'user_contact_email' in serializer.validated_data:
                email = serializer.validated_data['user_contact_email']
                contact, created = ContactsOpportunity.objects.get_or_create(email=email)
                if not created:
                    # Update existing contact (except for the email)
                    contact.name = serializer.validated_data.get('user_contact_name', contact.name)
                    contact.phone = serializer.validated_data.get('user_contact_phone', contact.phone)
                    contact.residency = serializer.validated_data.get('user_contact_residency', contact.residency)
                    contact.updated_by = request.user
                    contact.save()  # Save the updates to the existing contact
                else:
                    # Set additional fields for a newly created contact
                    contact.name = serializer.validated_data.get('user_contact_name')
                    contact.phone = serializer.validated_data.get('user_contact_phone')
                    contact.residency = serializer.validated_data.get('user_contact_residency')
                    contact.created_by = request.user
                    contact.save()  # Save the new contact details

                opportunity_service.user_contact = contact

            # update OpportunityServiceHistory object
            opportunity_service.save()


            # Prepare response data including ContactInfo details if created
            response_data = {
                "success": True,
                "statusCode": status.HTTP_201_CREATED,
                "data": {
                    "id": opportunity_service.id,
                    "name": opportunity_service.name.lower(),
                    "api_request": opportunity_service.api_request,
                    "api_response": opportunity_service.api_response,
                    "status": opportunity_service.status,
                    "start_date": opportunity_service.start_date,
                    "json_data": opportunity_service.json_data,
                    "user_contact": ContactSerializer(opportunity_service.user_contact).data
                }
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            print(e)
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class ContactListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        # Retrieve query parameters for email and broker_role
        email = request.query_params.get('email', None)
        phone = request.query_params.get('phone', None)
        name = request.query_params.get('name', None)
        
        contacts = ContactsOpportunity.objects.all()
        
        # Apply email filter if provided
        if email:
            contacts = contacts.filter(email__icontains=email)

        # Apply phone filter if provided
        if phone:
            contacts = contacts.filter(phone__icontains=phone)
        
        # Apply name filter if provided
        if name:
            contacts = contacts.filter(name__icontains=name)
        
        # Serialize the filtered queryset
        serializer = ContactSerializer(contacts, many=True)
        
        return Response({
            "success": True,
            "data": serializer.data
        },status=status.HTTP_200_OK)
    
    def post(self, request, *args, **kwargs):
        
        serializer = ContactSerializer(data=request.data)
       
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data.get('email')
        if ContactsOpportunity.objects.filter(name=email).exists():
            return Response({
                "error": "Contact with this name already exists."
            }, status=status.HTTP_400_BAD_REQUEST)

            
        try:
            contact_data = {
                'created_by': request.user,
                'email': email,
                'name': serializer.validated_data.get('name'),
                'phone': serializer.validated_data.get('phone'),
                'residency': serializer.validated_data.get('residency')
            }
            contact_opportunity = ContactsOpportunity.objects.create(**contact_data)
            # Create OpportunityServiceHistory object
            serializer = ContactSerializer(contact_opportunity)

            # Prepare response data including ContactInfo details if created
            response_data = {
                "success": True,
                "statusCode": status.HTTP_201_CREATED,
                "data": serializer.data
            }

            return Response(response_data, status=status.HTTP_201_CREATED)
        except Exception as e:
            print(e)
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
        
