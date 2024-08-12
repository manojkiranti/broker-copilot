from django.shortcuts import render
import base64
from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views  import APIView
from rest_framework.permissions import IsAuthenticated
from django.template.loader import render_to_string
from utils.renderers import html_to_pdf, html_to_pdf2
from weasyprint import HTML
from .models import SystemPrompt
from .serializers import UserContentSerializer, GenerateBrokerNotePdfSerializer
import requests
import os
# Create your views here.

class GenerateBrokerNoteAPIView(APIView):
     permission_classes = [IsAuthenticated]

     def post(self, request, *args, **kwargs):
        serializer = UserContentSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        user_content = serializer.validated_data['user_content']
        system_content_type = serializer.validated_data['broker_note_field']
        
        try:
            # Fetch the latest entry from SystemPrompt for the given compliance_field
            prompt = SystemPrompt.objects.values(system_content_type).latest('id')
            system_content = prompt[system_content_type]
        except SystemPrompt.DoesNotExist:
            return Response({"error": "System content not found"}, status=status.HTTP_404_NOT_FOUND)
        except KeyError:
            return Response({"error": "Invalid compliance field"}, status=status.HTTP_400_BAD_REQUEST)
 

        

        # system_content = SYSTEM_CONTENT.get(system_content_type, 'loan_objectives')
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
            
class GeneratePdfView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = GenerateBrokerNotePdfSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            context = {
                'name': serializer.validated_data.get('name', "")
            }
            # html_content = render_to_string('pdf_template.html', context)
            # pdf_content = html_to_pdf2("pdf_template.html", context)
            # if pdf_content is None:
            #     return Response("Invalid PDF", status=status.HTTP_400_BAD_REQUEST)
            
             # Generate the PDF
            # pdf = html_to_pdf2(html_content)
            
            html_string = render_to_string('pdf_template.html', context)

            # Convert HTML to PDF
            html = HTML(string=html_string)
            pdf = html.write_pdf()
        
            # Return the PDF as an HttpResponse
            response = HttpResponse(pdf, content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="document.pdf"'
            return response
        except Exception as e:
            return Response(
                {
                    "error": {
                        "statusCode": status.HTTP_400_BAD_REQUEST,
                        "message": str(e),
                    }
                }, status=status.HTTP_400_BAD_REQUEST
            )