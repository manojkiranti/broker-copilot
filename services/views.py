from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import BrokerServiceHistory, Service
from .serializers import BrokerServiceSerializer, BrokerServiceHistorySerializer, BrokerServiceHistoryUpdateSerializer

class BrokerServiceHistoryListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        tags=['Broker Service History']
    )
    def get(self, request, *args, **kwargs):
        try:
            broker_service_histories = BrokerServiceHistory.objects.filter(user=request.user)
            serializer = BrokerServiceSerializer(
                broker_service_histories, many=True)
            response_data = {
                "success": True,
                "statusCode": status.HTTP_200_OK,
                "data": serializer.data,
            }
            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class BrokerServiceHistoryRetrieveAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_id='retrieve_broker_service_history',
        tags=['Broker Service History'],
    )
    def get(self, request, pk, *args, **kwargs):
        try:
            broker_service_history = BrokerServiceHistory.objects.get(pk=pk, user=request.user)
            serializer = BrokerServiceHistorySerializer(broker_service_history)
            response_data = {
                "success": True,
                "statusCode": status.HTTP_200_OK,
                "data": serializer.data,
            }
            return Response(response_data, status=status.HTTP_200_OK)
        except BrokerServiceHistory.DoesNotExist:
            return Response({"error": "Broker service history not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class BrokerServiceHistoryCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=BrokerServiceHistorySerializer,
        operation_id='create_broker_service_history',
        tags=['Broker Service History'],
        responses={
            status.HTTP_201_CREATED: openapi.Response(
                description="Created",
                schema=BrokerServiceHistorySerializer,
            ),
            status.HTTP_400_BAD_REQUEST: openapi.Response(
                description="Bad Request"
            )
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = BrokerServiceHistorySerializer(data=request.data)
        if serializer.is_valid():
            try:
                broker_service = Service.objects.get(url='broker_service_history')

                broker_service_history_data = {
                    'user': request.user,
                    'service': broker_service,
                    'website_tracking_id': serializer.validated_data['website_tracking_id'],
                    'json_data': serializer.validated_data['json_data']
                }

                if 'api_request' in serializer.validated_data:
                    broker_service_history_data['api_request'] = serializer.validated_data['api_request']

                if 'api_response' in serializer.validated_data:
                    broker_service_history_data['api_response'] = serializer.validated_data['api_response']

                broker_service_history = BrokerServiceHistory.objects.create(**broker_service_history_data)
                response_data = {
                    "success": True,
                    "statusCode": status.HTTP_201_CREATED,
                    "data": {
                        "id": broker_service_history.id,
                        "website_tracking_id": broker_service_history.website_tracking_id,
                        "service": broker_service_history.service.name,
                        "api_request": broker_service_history.api_request,
                        "api_response": broker_service_history.api_response,
                        "status": broker_service_history.status,
                        "start_date": broker_service_history.start_date,
                        "json_data": broker_service_history.json_data
                    }
                }
                return Response(response_data, status=status.HTTP_201_CREATED)

            except Service.DoesNotExist:
                return Response({"error": "Broker service not found."}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BrokerServiceHistoryUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=BrokerServiceHistoryUpdateSerializer,
        operation_id='update_broker_service_history',
        tags=['Broker Service History'],
        responses={
            status.HTTP_200_OK: openapi.Response(
                description="Updated",
                schema=BrokerServiceHistoryUpdateSerializer,
            ),
            status.HTTP_404_NOT_FOUND: openapi.Response(
                description="Not Found"
            ),
            status.HTTP_400_BAD_REQUEST: openapi.Response(
                description="Bad Request"
            ),
            status.HTTP_500_INTERNAL_SERVER_ERROR: openapi.Response(
                description="Internal Server Error"
            )
        }
    )
    def put(self, request, *args, **kwargs):
        try:
            broker_service_history = BrokerServiceHistory.objects.get(pk=kwargs['pk'])
        except BrokerServiceHistory.DoesNotExist:
            return Response({"error": "Broker service history not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = BrokerServiceHistoryUpdateSerializer(broker_service_history, data=request.data, partial=True)
        if serializer.is_valid():
            try:
                broker_service_history.json_data = serializer.validated_data.get('json_data', broker_service_history.json_data)

                if 'api_request' in serializer.validated_data:
                    broker_service_history.api_request = serializer.validated_data['api_request']

                if 'api_response' in serializer.validated_data:
                    broker_service_history.api_response = serializer.validated_data['api_response']

                broker_service_history.save()

                # Construct response with selected fields
                response_data = {
                    "id": broker_service_history.id,
                    "service": broker_service_history.service.name,
                    "api_request": broker_service_history.api_request,
                    "api_response": broker_service_history.api_response,
                    "status": broker_service_history.status,
                    "start_date": broker_service_history.start_date,
                    "json_data": broker_service_history.json_data
                }

                return Response(response_data, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)