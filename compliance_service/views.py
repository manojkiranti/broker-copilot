from rest_framework.response import Response
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from rest_framework import status
from rest_framework.views  import APIView
from django.db import transaction
from rest_framework.permissions import IsAuthenticated
from accounts.permissions import IsAdminUser
from compliance_service.serializers import UserContentSerializer, ComplianceNoteSerializer, ComplianceOpportunitySerializer, SystemPromptSerializer
from .data.content import SYSTEM_CONTENT
from .models import SystemPrompt, Note, ComplianceSystemPrompt
from opportunity_app.models import Opportunity
import requests
import os


# Create your views here.
class ComplianceNoteListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        try:
            notes_query = Note.objects.filter(status='active').order_by('-updated_at')
            # Check for 'latest' query parameter
            if request.query_params.get('latest') == 'true':
                notes_query = notes_query[:3]  # Limit to latest 3 notes
            serializer = ComplianceNoteSerializer(notes_query, many=True)
            response_data = {
                "success": True,
                "statusCode": status.HTTP_200_OK,
                "data": serializer.data,
            }
            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)    
        
    def post(self, request, *args, **kwargs):
        serializer = ComplianceNoteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        
        try:
            with transaction.atomic():
                opportunity_id = serializer.validated_data['opportunity_id']
                opportunity = Opportunity.objects.filter(id=opportunity_id).first()
                if not opportunity:
                    return Response({
                        "error": {
                            "statusCode": status.HTTP_400_BAD_REQUEST,
                            "message": "A deal with the given id does not exist",
                        }
                    }, status=status.HTTP_400_BAD_REQUEST)
                    
                opp_data_serializer = ComplianceOpportunitySerializer(data=serializer.validated_data.get('opportunity_data', {}))

                if opp_data_serializer.is_valid():
                    updated_json_data = opportunity.json_data
                    updated_json_data.update(opp_data_serializer.validated_data)
                    opportunity.json_data = updated_json_data
                    opportunity.save()
                
                note_data = {
                    'document_identification_method': serializer.validated_data.get('document_identification_method'),
                    'client_interview_method': serializer.validated_data.get('client_interview_method'),
                    'credit_guide_provided': serializer.validated_data.get('credit_guide_provided'),
                    'estimated_settlement_date': serializer.validated_data.get('estimated_settlement_date'),
                    'facility_amount': serializer.validated_data.get('facility_amount'),
                    'rate_type': serializer.validated_data.get('rate_type'),
                    'repayment_type': serializer.validated_data.get('repayment_type'),
                    'repayment_frequency': serializer.validated_data.get('repayment_frequency'),
                    'offset': serializer.validated_data.get('offset'),
                    'cash_out_involved': serializer.validated_data.get('cash_out_involved'),
                    'loan_structure': serializer.validated_data.get('loan_structure'),
                    'loan_scenario_lender_1': serializer.validated_data.get('loan_scenario_lender_1'),
                    'loan_scenario_lender_2': serializer.validated_data.get('loan_scenario_lender_2'),
                    'loan_scenario_lender_3': serializer.validated_data.get('loan_scenario_lender_3'),
                    'loan_objective_note': serializer.validated_data.get('loan_objective_note'),
                    'loan_requirement_note': serializer.validated_data.get('loan_requirement_note'),
                    'loan_circumstances_note': serializer.validated_data.get('loan_circumstances_note'),
                    'loan_financial_awareness_note': serializer.validated_data.get('loan_financial_awareness_note'),
                    'loan_structure_note': serializer.validated_data.get('loan_structure_note'),
                    'loan_prioritised_note': serializer.validated_data.get('loan_prioritised_note'),
                    'lender_loan_note': serializer.validated_data.get('lender_loan_note'),
                    'status': 'active',
                    'opportunity_id': opportunity_id,
                    
                    'created_by_id': request.user.id,
                    'updated_by_id': request.user.id,
                }
                note = Note.objects.create(**note_data)
                serializer_data = ComplianceNoteSerializer(note)
                response_data = {
                    "success": True,
                    "statusCode": status.HTTP_201_CREATED,
                    "data": serializer_data.data,
                }

                return Response(response_data, status=status.HTTP_201_CREATED)
        except Exception as e:
            # logger.error(f"Error creating opportunity: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ComplianceNoteDetailUpdateDeleteAPIView(APIView):
     permission_classes = [IsAuthenticated]
     
     def get(self, request, pk, *args, **kwargs):
         try:
             note = Note.objects.get(pk=pk, status='active')
             serializer = ComplianceNoteSerializer(note)
             response_data = {
                 "success": True,
                 "statusCode": status.HTTP_200_OK,
                 "data": serializer.data,
             }
             return Response(response_data, status=status.HTTP_200_OK)
         except Note.DoesNotExist:
            return Response({"error": "Compliance Note with the given id not found."}, status=status.HTTP_404_NOT_FOUND)
         except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
     def delete(self, request, pk, *args, **kwargs):
        note = Note.objects.get( pk=pk)
        if not note:
            return Response({"error": "Compliance note not found."}, status=status.HTTP_404_NOT_FOUND)
        
        if request.user != note.created_by:
            return Response({"error": "You don't have permission to delete this Compliance Note."}, status=status.HTTP_403_FORBIDDEN)
        
        try:
            # Set status to 'inactive' to soft delete the service
            note.status = 'inactive'
            note.save()
        except (ValidationError, IntegrityError) as e:
            # Handle specific database errors
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            "success": True,
            "statusCode": status.HTTP_200_OK,
            "message": "Successfully deleted compliance note"
        }, status=status.HTTP_200_OK)
    
     def patch(self, request, pk, *args, **kwargs):
        note = Note.objects.get( pk=pk)
        if not note:
            return Response({"error": "Compliance note not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = ComplianceNoteSerializer(note, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        if request.user != note.created_by:
            return Response({"error": "You don't have permission to update this Compliance Note."}, status=status.HTTP_403_FORBIDDEN)
        
        try:
            with transaction.atomic():
                opportunity = note.opportunity
                    
                opp_data_serializer = ComplianceOpportunitySerializer(data=serializer.validated_data.get('opportunity_data', {}))
                if opp_data_serializer.is_valid():
                    updated_json_data = opportunity.json_data
                    updated_json_data.update(opp_data_serializer.validated_data)
                    opportunity.json_data = updated_json_data
                    opportunity.save()
             
                note.updated_by = request.user
                note.document_identification_method = serializer.validated_data.get('document_identification_method')
                note.client_interview_method = serializer.validated_data.get('client_interview_method')
                note.credit_guide_provided = serializer.validated_data.get('credit_guide_provided')
                note.estimated_settlement_date = serializer.validated_data.get('estimated_settlement_date')
                note.facility_amount = serializer.validated_data.get('facility_amount')
                note.rate_type = serializer.validated_data.get('rate_type')
                note.repayment_type = serializer.validated_data.get('repayment_type')
                note.repayment_frequency = serializer.validated_data.get('repayment_frequency')
                note.offset = serializer.validated_data.get('offset')
                note.cash_out_involved = serializer.validated_data.get('cash_out_involved')
                note.loan_structure = serializer.validated_data.get('loan_structure')
                note.loan_scenario_lender_1 = serializer.validated_data.get('loan_scenario_lender_1')
                note.loan_scenario_lender_2 = serializer.validated_data.get('loan_scenario_lender_2')
                note.loan_scenario_lender_3 = serializer.validated_data.get('loan_scenario_lender_3')
                note.loan_objective_note = serializer.validated_data.get('loan_objective_note')
                note.loan_requirement_note = serializer.validated_data.get('loan_requirement_note')
                note.loan_circumstances_note = serializer.validated_data.get('loan_circumstances_note')
                note.loan_financial_awareness_note = serializer.validated_data.get('loan_financial_awareness_note')
                note.loan_structure_note = serializer.validated_data.get('loan_structure_note')
                note.loan_prioritised_note = serializer.validated_data.get('loan_prioritised_note')
                note.lender_loan_note = serializer.validated_data.get('lender_loan_note')
                note.opportunity = opportunity
                note.save()
                
                serializer_data = ComplianceNoteSerializer(note)
                response_data = {
                    "success": True,
                    "statusCode": status.HTTP_200_OK,
                    "data": serializer_data.data,
                }

                return Response(response_data, status=status.HTTP_200_OK)
        except ValidationError as e:  # Specific exceptions can be more useful
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GenerateComplianceNoteAPIView(APIView):
     permission_classes = [IsAuthenticated]

     def post(self, request, *args, **kwargs):
        serializer = UserContentSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        user_content = serializer.validated_data['user_content']
        system_content_type = serializer.validated_data['compliance_field']
        
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

class GenerateComplianceNoteV2APIView(APIView):
     permission_classes = [IsAuthenticated]

     def post(self, request, *args, **kwargs):
        serializer = UserContentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_content = serializer.validated_data['user_content']
        system_content_type = serializer.validated_data['compliance_field']
        
        try:
            # Fetch the latest entry from SystemPrompt for the given compliance_field
            system_prompt = ComplianceSystemPrompt.objects.get(prompt_type=system_content_type)
            system_content = system_prompt.prompt

        except ComplianceSystemPrompt.DoesNotExist:
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

class SystemPromptListAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            system_prompts = ComplianceSystemPrompt.objects.all()
            serializer = SystemPromptSerializer(system_prompts, many=True)
            response_data = {
                "success": True,
                "statusCode": status.HTTP_200_OK,
                "data": serializer.data,
            }
            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 
        
class SystemPromptPatchAPIView(APIView):
    permission_classes = [IsAdminUser]
    
    def patch(self, request, pk):
        try:
            prompt_instance = ComplianceSystemPrompt.objects.get(pk=pk)
        except ComplianceSystemPrompt.DoesNotExist:
            return Response({"error": "System prompt not found"}, status=status.HTTP_404_NOT_FOUND)
        prompt_data = request.data.get('prompt', None)
        if prompt_data is not None:            
            prompt_instance.prompt = prompt_data
            prompt_instance.save()
            response_data = {
                        "success": True,
                        "statusCode": status.HTTP_200_OK,
                        "data": SystemPromptSerializer(prompt_instance).data
                        }
            return Response(response_data, status=status.HTTP_200_OK)