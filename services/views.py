from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import BrokerServiceHistory, BrokerServiceHistoryDetail, Service
from .serializers import BrokerServiceHistoryDetailSerializer

class BrokerServiceHistoryDetailCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        data = request.data
        try:
            broker_service_history = BrokerServiceHistory.objects.get(pk=data['broker_service_history'])
            broker_service_history.user = request.user
            broker_service_history.save()
        except BrokerServiceHistory.DoesNotExist:
            # Create a new BrokerServiceHistory instance if it does not exist
            service = Service.objects.get(pk=data['service'])
            broker_service_history = BrokerServiceHistory.objects.create(
                user=request.user,
                service=service,
                status=data.get('status', 'default_status')
            )
        
        # Set the broker_service_history in the data
        data['broker_service_history'] = broker_service_history.id

        # Create the BrokerServiceHistoryDetail instance
        serializer = BrokerServiceHistoryDetailSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
