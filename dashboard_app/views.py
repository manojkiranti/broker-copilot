from django.shortcuts import render
from rest_framework.views import APIView
from django.db.models import Q
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from opportunity_app.models import ContactsOpportunity, Opportunity
from compliance_service.models import Note as ComplianceNote
from broker_service.models import Note as BrokerNote
# Create your views here.


class DashboardListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        current_user = request.user
        opportunity_count = Opportunity.objects.filter(
            Q(primary_processor=current_user) |
            Q(secondary_processor=current_user) |
            Q(created_by=current_user)
        ).count()
        contact_count = ContactsOpportunity.objects.count()
        compliance_note_count = ComplianceNote.objects.filter(
            Q(opportunity__primary_processor=current_user) |
            Q(opportunity__secondary_processor=current_user) |
            Q(opportunity__created_by=current_user)
        ).count()
        broker_note_count = BrokerNote.objects.filter(
            Q(opportunity__primary_processor=current_user) |
            Q(opportunity__secondary_processor=current_user) |
            Q(opportunity__created_by=current_user)
        ).count()

        response_data = {
            "success": True,
            "statusCode": status.HTTP_200_OK,
            "data": {
                'opportunity_count': opportunity_count,
                'contact_count': contact_count,
                'compliance_note_count': compliance_note_count,
                'broker_note_count': broker_note_count
            }
        }
        return Response(response_data, status=status.HTTP_200_OK)
