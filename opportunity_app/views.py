from rest_framework.response import Response
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
import logging
from django.db import transaction
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

logger = logging.getLogger(__name__)

User = get_user_model()

class OpportunityListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
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

        try:
            with transaction.atomic():
                # Check if name already exists
                name = serializer.validated_data.get('name')
                if Opportunity.objects.filter(name=name).exists():
                    return Response({
                        "error": "An opportunity with this name already exists."
                    }, status=status.HTTP_400_BAD_REQUEST)

                # Check if website_tracking_id already exists
                website_tracking_id = serializer.validated_data.get('website_tracking_id')
                if website_tracking_id and Opportunity.objects.filter(website_tracking_id=website_tracking_id).exists():
                    return Response({
                        "error": "An opportunity with this website tracking ID already exists."
                    }, status=status.HTTP_400_BAD_REQUEST)

                # Create Opportunity
                opportunity = Opportunity.objects.create(
                    name=name,
                    type=serializer.validated_data['type'],
                    website_tracking_id=website_tracking_id,
                    json_data=serializer.validated_data.get('json_data', {}),
                    created_by=request.user,
                )
                
                # Associate Primary Contact
                primary_contact_data = serializer.validated_data.pop('primary_contact', None)
                if primary_contact_data:
                    primary_contact, created = ContactsOpportunity.objects.get_or_create(email=primary_contact_data['email'], defaults=primary_contact_data)
                    if not created:
                        for key, value in primary_contact_data.items():
                            if key != 'email':  # Avoid updating the unique identifier
                                setattr(primary_contact, key, value)
                        primary_contact.save()
                    opportunity.primary_contact = primary_contact
                
                
                # Associate Secondary Contacts
                secondary_contact_data = serializer.validated_data.pop('secondary_contact', None)
                if secondary_contact_data:
                    secondary_contact, created = ContactsOpportunity.objects.get_or_create(
                        email=secondary_contact_data['email'],
                        defaults=secondary_contact_data
                    )
                    if not created:
                        # Update the fields if the contact already existed
                        for key, value in secondary_contact_data.items():
                            if key != 'email':  # Avoid updating the unique identifier
                                setattr(secondary_contact, key, value)
                        secondary_contact.save()
                    opportunity.secondary_contact = secondary_contact

                # Update Primary Processor
                primary_processor_data = serializer.validated_data.get('primary_processor')
                if primary_processor_data:
                    primary_processor = get_object_or_404(User, email=primary_processor_data)
                    opportunity.primary_processor = primary_processor

                # Update Secondary Processor
                secondary_processor_data = serializer.validated_data.get('secondary_processor')
                if secondary_processor_data:
                    secondary_processor = get_object_or_404(User, email=secondary_processor_data)
                    opportunity.secondary_processor = secondary_processor

                opportunity.save()

                # Prepare response data
                response_data = {
                    "success": True,
                    "statusCode": status.HTTP_201_CREATED,
                    "data": {
                        "id": opportunity.id,
                        "name": opportunity.name,
                    }
                }

                return Response(response_data, status=status.HTTP_201_CREATED)

        except Exception as e:
            # logger.error(f"Error creating opportunity: {str(e)}")
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
        opportunity = self.get_object(pk)
        if not opportunity:
            return Response({"error": "Deals not found."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = OpportunitySerializer(data=request.data)
       
        serializer.is_valid(raise_exception=True)
        if request.user != opportunity.created_by and \
             request.user != opportunity.primary_contact and \
             request.user != opportunity.secondary_contact:
            return Response({"error": "You don't have permission to update this Deals."}, status=status.HTTP_403_FORBIDDEN)
        
        name = serializer.validated_data.get('name')
        if Opportunity.objects.filter(name=name).exclude(pk=opportunity.pk).exists():
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
            with transaction.atomic():
                opportunity.name = name
                opportunity.type = serializer.validated_data.get('type')
                opportunity.website_tracking_id = website_tracking_id
                opportunity.json_data = serializer.validated_data.get('json_data', {})

                # Associate Primary Contact
                primary_contact_data = serializer.validated_data.pop('primary_contact', None)
                if primary_contact_data:
                    primary_contact, created = ContactsOpportunity.objects.get_or_create(email=primary_contact_data['email'], defaults=primary_contact_data)
                    if not created:
                        for key, value in primary_contact_data.items():
                            if key != 'email':  # Avoid updating the unique identifier
                                setattr(primary_contact, key, value)
                        primary_contact.save()
                    opportunity.primary_contact = primary_contact
                        
                
                    
                 # Associate Secondary Contacts
                secondary_contact_data = serializer.validated_data.pop('secondary_contact', None)
                if secondary_contact_data:
                    secondary_contact, created = ContactsOpportunity.objects.get_or_create(
                        email=secondary_contact_data['email'],
                        defaults=secondary_contact_data
                    )
                    if not created:
                        # Update the fields if the contact already existed
                        for key, value in secondary_contact_data.items():
                            if key != 'email':  # Avoid updating the unique identifier
                                setattr(secondary_contact, key, value)
                        secondary_contact.save()
                    opportunity.secondary_contact = secondary_contact

                # Update Primary Processor
                primary_processor_data = serializer.validated_data.get('primary_processor')
                if primary_processor_data:
                    primary_processor = get_object_or_404(User, email=primary_processor_data)
                    opportunity.primary_processor = primary_processor

                # Update Secondary Processor
                secondary_processor_data = serializer.validated_data.get('secondary_processor')
                if secondary_processor_data:
                    secondary_processor = get_object_or_404(User, email=secondary_processor_data)
                    opportunity.secondary_processor = secondary_processor

                opportunity.save()
                
                # Prepare response data including ContactInfo details if created
                response_data = {
                    "success": True,
                    "statusCode": status.HTTP_201_CREATED,
                    "data": {
                        "id": opportunity.id,
                        "name": opportunity.name.lower()
                    }
                }

                return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            print(e)
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class ContactListCreateUpdateAPIView(APIView):
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
        
    def patch(self, request, *args, **kwargs):
        email = request.data.get('email')
        if not email:
            return Response({"error": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)

        contact, created = ContactsOpportunity.objects.get_or_create(email=email)
        serializer = ContactSerializer(contact, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            # Exclude email from being updated, even if included in the request
            validated_data = {k: v for k, v in serializer.validated_data.items() if k != 'email'}
            for key, value in validated_data.items():
                setattr(contact, key, value)
            
            contact.updated_by = request.user
            contact.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

class ContactDetailUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def put(self, request, *args, **kwargs):
        contact_id = kwargs.get('pk')
        contact = get_object_or_404(ContactsOpportunity, pk=contact_id)
        
        serializer = ContactSerializer(contact, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save(updated_by=request.user)
            return Response({
                "success": True,
                "statusCode": status.HTTP_200_OK,
                "data": serializer.data
            })

    def delete(self, request, *args, **kwargs):
        contact_id = kwargs.get('pk')
        contact = get_object_or_404(ContactsOpportunity, pk=contact_id)
        contact.status = ContactsOpportunity.OpportunityStatus.INACTIVE
        contact.save(update_fields=['status'])

        return Response({
            "success": True,
            "statusCode": status.HTTP_204_NO_CONTENT,
            "message": "Contact has been deleted."
        })

class ContactCheckAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        
        # Check if the email is provided
        if not email:
            return Response({"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        contact = ContactsOpportunity.objects.filter(email=email).first()
        
        if contact:
            # If contact exists, return the data
            serializer = ContactSerializer(contact)
            return Response({
                "success": True,
                "statusCode": status.HTTP_200_OK,
                "data": serializer.data
            })
        else:
            # If contact doesn't exist, create a new one
            serializer = ContactSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
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
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)