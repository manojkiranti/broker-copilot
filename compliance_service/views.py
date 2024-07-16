from rest_framework.response import Response
from rest_framework import status
from rest_framework.views  import APIView
from rest_framework.permissions import IsAuthenticated
from compliance_service.serializers import UserContentSerializer
from .data.content import SYSTEM_CONTENT
import requests
import os


# Create your views here.

class GenerateComplianceNoteAPIView(APIView):
    #  permission_classes = [IsAuthenticated]

     def post(self, request, *args, **kwargs):
        serializer = UserContentSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        user_content = serializer.validated_data['user_content']
        system_content_type = serializer.validated_data['compliance_field']

        system_content = SYSTEM_CONTENT.get(system_content_type, 'loan_objectives')
        # Set up the header with your OpenAI API Key
        bearer_token = os.getenv('OPEN_AI_KEY')
        temperature = float(os.getenv('OPEN_AI_TEMPERATURE'))
        OPEN_AI_URL = os.getenv('OPEN_AI_URL')
        GPT_MODEL = os.getenv('GPT_MODEL')
        
        headers = {
            'Authorization': f'Bearer {bearer_token}',
            'Content-Type': 'application/json'
        }

        # The body of your request to OpenAI
        data = {
            "model": GPT_MODEL,
            "messages": [
                {
                    "role": "system",
                    "content": system_content
                },
                {
                  "role": "user",
                  "content": user_content
                }
            ],
            "temperature":temperature
        }

        # The endpoint URL
        url = OPEN_AI_URL

        # Make the POST request
        response = requests.post(url, json=data, headers=headers)

        # Check if the request was successful
        if response.status_code == 200:
            # Return the content of the response from OpenAI
            response_data = {
                    "success": True,
                    "statusCode": status.HTTP_200_OK,
                    "data":  response.json()
                    }
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            # If the call was unsuccessful, return an error status
            return Response({
                "message": "Failed to generate compliance note",
                "status_code": response.status_code,
                "error": response.text
            }, status=status.HTTP_400_BAD_REQUEST)
        