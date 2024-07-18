import base64
from rest_framework.response import Response
from django.db.models import Q
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from utils.renderers import html_to_pdf

from .serializers import GeneratePdfSerializer, OpportunityServiceSerializer, ContactSerializer
from .models import OpportunityService, ContactsOpportunity
from services.models import Service
from django.contrib.auth import get_user_model

User = get_user_model()


class OpportunityServiceListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        search_query = request.query_params.get('name', '')
        try:
            # Filter OpportunityService objects by search query if provided
            if search_query:
                opportunity_services = OpportunityService.objects.filter(
                    Q(user=request.user) & Q(name__icontains=search_query)
                )
            else:
                opportunity_services = OpportunityService.objects.filter(
                    user=request.user)
            serializer = OpportunityServiceSerializer(
                opportunity_services, many=True)
            response_data = {
                "success": True,
                "statusCode": status.HTTP_200_OK,
                "data": serializer.data,
            }
            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class OpportunityServiceCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = OpportunityServiceSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)
        website_tracking_id = serializer.validated_data.get(
            'website_tracking_id')

        # Check if website_tracking_id already exists
        if website_tracking_id and OpportunityService.objects.filter(website_tracking_id=website_tracking_id).exists():
            return Response({
                "error": "An opportunity with this website tracking ID already exists."
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            opportunity_service_history_data = {
                'user': request.user,
                'name': serializer.validated_data['name'],
                'type': serializer.validated_data['type'],
                'website_tracking_id': serializer.validated_data.get('website_tracking_id'),
                'json_data': serializer.validated_data.get('json_data', {}),
                'api_request': serializer.validated_data.get('api_request', {}),
                'api_response': serializer.validated_data.get('api_response', {})
            }

            # Handling optional primary_contact
            primary_contact_id = serializer.validated_data.get(
                'primary_contact_id')
            if primary_contact_id:
                primary_contact = User.objects.filter(
                    id=primary_contact_id).first()
                if primary_contact:
                    opportunity_service_history_data['primary_contact'] = primary_contact

            # Handling optional secondary_contact
            secondary_contact_id = serializer.validated_data.get(
                'secondary_contact_id')
            if secondary_contact_id:
                secondary_contact = User.objects.filter(
                    id=secondary_contact_id).first()
                if secondary_contact:
                    opportunity_service_history_data['secondary_contact'] = secondary_contact

            # Check if any user contact info fields are present in the serializer data
            # Handling ContactsOpportunity relationship if provided
            if 'user_contact_email' in serializer.validated_data:
                email = serializer.validated_data['user_contact_email']
                contact, created = ContactsOpportunity.objects.get_or_create(
                    email=email)
                if not created:
                    # Update existing contact (except for the email)
                    contact.name = serializer.validated_data.get(
                        'user_contact_name', contact.name)
                    contact.phone = serializer.validated_data.get(
                        'user_contact_phone', contact.phone)
                    contact.identity_number = serializer.validated_data.get(
                        'user_contact_identity_number', contact.identity_number)
                    contact.save()  # Save the updates to the existing contact
                else:
                    # Set additional fields for a newly created contact
                    contact.name = serializer.validated_data.get(
                        'user_contact_name')
                    contact.phone = serializer.validated_data.get(
                        'user_contact_phone')
                    contact.identity_number = serializer.validated_data.get(
                        'user_contact_identity_number')
                    contact.save()  # Save the new contact details

                opportunity_service_history_data['user_contact'] = contact

            # Create OpportunityServiceHistory object
            opportunity_service_history = OpportunityService.objects.create(
                **opportunity_service_history_data)

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


class OpportunityServiceUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return OpportunityService.objects.get(pk=pk)
        except OpportunityService.DoesNotExist:
            return None

    def put(self, request, pk, *args, **kwargs):
        opportunity_service = self.get_object(pk)
        if not opportunity_service:
            return Response({"error": "OpportunityService not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = OpportunityServiceSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)
        website_tracking_id = serializer.validated_data.get(
            'website_tracking_id')

        # Check for website_tracking_id uniqueness except for the current instance
        website_tracking_id = serializer.validated_data.get(
            'website_tracking_id')
        if website_tracking_id:
            if OpportunityService.objects.filter(website_tracking_id=website_tracking_id).exclude(pk=pk).exists():
                return Response({
                    "error": "An opportunity with this website tracking ID already exists."
                }, status=status.HTTP_400_BAD_REQUEST)

        try:

            opportunity_service.name = serializer.validated_data.get('name')
            opportunity_service.type = serializer.validated_data.get('type')
            opportunity_service.website_tracking_id = serializer.validated_data.get(
                'website_tracking_id')
            opportunity_service.json_data = serializer.validated_data.get(
                'json_data', {})
            opportunity_service.api_request = serializer.validated_data.get(
                'api_request', {})
            opportunity_service.api_response = serializer.validated_data.get(
                'api_response', {})
            # Handling optional primary_contact
            primary_contact_id = serializer.validated_data.get(
                'primary_contact_id')
            if primary_contact_id:
                primary_contact = User.objects.filter(
                    id=primary_contact_id).first()
                if primary_contact:
                    opportunity_service['primary_contact'] = primary_contact

            # Handling optional secondary_contact
            secondary_contact_id = serializer.validated_data.get(
                'secondary_contact_id')
            if secondary_contact_id:
                secondary_contact = User.objects.filter(
                    id=secondary_contact_id).first()
                if secondary_contact:
                    opportunity_service['secondary_contact'] = secondary_contact

            # Check if any user contact info fields are present in the serializer data
            # Handling ContactsOpportunity relationship if provided
            if 'user_contact_email' in serializer.validated_data:
                email = serializer.validated_data['user_contact_email']
                contact, created = ContactsOpportunity.objects.get_or_create(
                    email=email)
                if not created:
                    # Update existing contact (except for the email)
                    contact.name = serializer.validated_data.get(
                        'user_contact_name', contact.name)
                    contact.phone = serializer.validated_data.get(
                        'user_contact_phone', contact.phone)
                    contact.identity_number = serializer.validated_data.get(
                        'user_contact_identity_number', contact.identity_number)
                    contact.save()  # Save the updates to the existing contact
                else:
                    # Set additional fields for a newly created contact
                    contact.name = serializer.validated_data.get(
                        'user_contact_name')
                    contact.phone = serializer.validated_data.get(
                        'user_contact_phone')
                    contact.identity_number = serializer.validated_data.get(
                        'user_contact_identity_number')
                    contact.save()  # Save the new contact details

                opportunity_service['user_contact'] = contact

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


class OpportunityServiceListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        search_query = request.query_params.get('name', '')
        try:
            # Filter OpportunityService objects by search query if provided
            if search_query:
                opportunity_services = OpportunityService.objects.filter(
                    Q(user=request.user) & Q(name__icontains=search_query)
                )
            else:
                opportunity_services = OpportunityService.objects.filter(
                    user=request.user)
            serializer = OpportunityServiceSerializer(
                opportunity_services, many=True)
            response_data = {
                "success": True,
                "statusCode": status.HTTP_200_OK,
                "data": serializer.data,
            }
            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class OpportunityServiceDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk, *args, **kwargs):
        try:
            opportunity_service_history = OpportunityService.objects.get(
                pk=pk, user=request.user)
            serializer = OpportunityServiceSerializer(
                opportunity_service_history)
            response_data = {
                "success": True,
                "statusCode": status.HTTP_200_OK,
                "data": serializer.data,
            }
            return Response(response_data, status=status.HTTP_200_OK)
        except OpportunityService.DoesNotExist:
            return Response({"error": "Opportunity service history not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GeneratePdfView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=GeneratePdfSerializer,
        tags=['Broker Service History'],
    )
    def post(self, request, *args, **kwargs):
        serializer = GeneratePdfSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            context = {
                'data': serializer.validated_data['json_data']
            }
            pdf_content = html_to_pdf("pdf_template.html", context)
            if pdf_content is None:
                return Response("Invalid PDF", status=status.HTTP_400_BAD_REQUEST)

            pdf_base64 = base64.b64encode(pdf_content).decode('utf-8')
            pdf_data_url = f"data:application/pdf;base64,{pdf_base64}"

            data = {
                "pdfUrl": pdf_data_url,
                "content_type": "application/pdf"
            }
            response_data = {
                "success": True,
                "statusCode": status.HTTP_200_OK,
                "data": data,
            }
            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {
                    "error": {
                        "statusCode": status.HTTP_400_BAD_REQUEST,
                        "message": str(e),
                    }
                }, status=status.HTTP_400_BAD_REQUEST
            )
