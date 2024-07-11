from rest_framework.response import Response
from rest_framework import status
from rest_framework.views  import APIView
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .serializers import OpportunityServiceSerializer
from .models import OpportunityService
from services.models import Service

class OpportunityServiceListAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        tags=['Broker Service History']
    )
    def get(self, request, *args, **kwargs):
        try:
            broker_service_list = OpportunityService.objects.filter(user=request.user)
            serializer = OpportunityServiceSerializer(
                broker_service_list, many=True)
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

    @swagger_auto_schema(
        request_body=OpportunityServiceSerializer,
        operation_id='create_opportunity_service_history',
        tags=['Opportunity Service History'],
        responses={
            status.HTTP_201_CREATED: openapi.Response(
                description="Created",
                schema=OpportunityServiceSerializer,
            ),
            status.HTTP_400_BAD_REQUEST: openapi.Response(
                description="Bad Request"
            )
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = OpportunityServiceSerializer(data=request.data)
        if serializer.is_valid():
            try:
                opportunity_service = Service.objects.get(url='opportunity_service_history')

                opportunity_service_history_data = {
                    'user': request.user,
                    'service': opportunity_service,
                    # 'website_tracking_id': serializer.validated_data['website_tracking_id'],
                    'json_data': serializer.validated_data['json_data']
                }

                if 'api_request' in serializer.validated_data:
                    opportunity_service_history_data['api_request'] = serializer.validated_data['api_request']

                if 'api_response' in serializer.validated_data:
                    opportunity_service_history_data['api_response'] = serializer.validated_data['api_response']

                opportunity_service_history = OpportunityService.objects.create(**opportunity_service_history_data)
                response_data = {
                    "success": True,
                    "statusCode": status.HTTP_201_CREATED,
                    "data": {
                        "id": opportunity_service_history.id,
                        # "website_tracking_id": opportunity_service_history.website_tracking_id,
                        "service": opportunity_service_history.service.name,
                        "api_request": opportunity_service_history.api_request,
                        "api_response": opportunity_service_history.api_response,
                        "status": opportunity_service_history.status,
                        "start_date": opportunity_service_history.start_date,
                        "json_data": opportunity_service_history.json_data
                    }
                }
                return Response(response_data, status=status.HTTP_201_CREATED)

            except Service.DoesNotExist:
                return Response({"error": "Opportunity service not found."}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class OpportunityServiceDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(
        request_body=OpportunityServiceSerializer,
        operation_id='get_opportunity_service_detail',
        tags=['Opportunity Service Details'],
        responses={
            status.HTTP_201_CREATED: openapi.Response(
                description="Created",
                schema=OpportunityServiceSerializer,
            ),
            status.HTTP_400_BAD_REQUEST: openapi.Response(
                description="Bad Request"
            )
        }
    )
    def get(self, request, pk, *args, **kwargs):
        try:
            opportunity_service_history = OpportunityService.objects.get(pk=pk, user=request.user)
            serializer = OpportunityServiceSerializer(opportunity_service_history)
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
        
        