from django.shortcuts import render
from rest_framework.views  import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from opportunity_app.models import ContactsOpportunity, Opportunity
from compliance_service.models import Note
# Create your views here.

class DashboardListAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        opportunity_count = Opportunity.objects.count()
        contact_count = ContactsOpportunity.objects.count()
        compliance_note_count = Note.objects.count()
        
        response_data = {
                "success": True,
                "statusCode": status.HTTP_200_OK,
                "data": {
                    'opportunity_count': opportunity_count,
                    'contact_count': contact_count,
                    'compliance_note_count': compliance_note_count
                }
            }
        return Response(response_data, status=status.HTTP_200_OK)