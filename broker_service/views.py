from django.shortcuts import render
import base64
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views  import APIView
from rest_framework.permissions import IsAuthenticated
from accounts.permissions import IsAdminUser
from django.template.loader import render_to_string
from utils.renderers import html_to_pdf
from django.db import transaction
from utils.common_utils import split_name
from .models import SystemPrompt, Note, BrokerNoteSystemprompt
from opportunity_app.models import Opportunity
from .serializers import UserContentSerializer, GenerateBrokerNotePdfSerializer, BrokerNoteSerializer, SystemPromptSerializer
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
            
class GenerateBrokerNoteV2APIView(APIView):
     permission_classes = [IsAuthenticated]

     def post(self, request, *args, **kwargs):
        serializer = UserContentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_content = serializer.validated_data['user_content']
        system_content_type = serializer.validated_data['broker_note_field']
        
        try:
            # Fetch the latest entry from SystemPrompt for the given compliance_field
            system_prompt = BrokerNoteSystemprompt.objects.get(prompt_type=system_content_type)
            system_content = system_prompt.prompt
        except BrokerNoteSystemprompt.DoesNotExist:
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
            
            # Accessing nested broker detail data
            processor_data = serializer.validated_data.get('processor', {})
            processor_name = processor_data.get('name', "")
            processor_email = processor_data.get('email', "")
            processor_phone = processor_data.get('phone', "")
            
            # Accessing nested processor detail data
            secondary_processor_data = serializer.validated_data.get('secondary_processor', {})
            secondary_processor_name = secondary_processor_data.get('name', "")
            secondary_processor_email = secondary_processor_data.get('email', "")
            secondary_processor_phone = secondary_processor_data.get('phone', "")
            
            # Accessing primary contact data
            primary_contact_data = serializer.validated_data.get('primary_contact', {})
            primary_contact_name = primary_contact_data.get('name', "")
            primary_contact_citizenship = primary_contact_data.get('citizenship', "")
            primary_contact_residency = primary_contact_data.get('residency', "")
            primary_contact_occupation = primary_contact_data.get('occupation', "")
            primary_contact_employer = primary_contact_data.get('employer', "")
            
            frist_name, last_name = split_name(primary_contact_name)
            
            # Accessing primary contact data
            secondary_contact_data = serializer.validated_data.get('secondary_contact', {})
            secondary_contact_name = secondary_contact_data.get('name', "")
            secondary_contact_citizenship = secondary_contact_data.get('citizenship', "")
            secondary_contact_residency = secondary_contact_data.get('residency', "")
            secondary_contact_occupation = secondary_contact_data.get('occupation', "")
            secondary_contact_employer = secondary_contact_data.get('employer', "")

            frist_name_2, last_name_2 = split_name(secondary_contact_name)
            
            default_loan_detail = {
                'finance_due_date': '',
                'settlement_date': '',
                'lender': '',
                'loan_term': '',
                'property_value': '',
                'interest_rate': '',
                'loan_purpose': '',
                'loan_amount': '',
                'product': '',
                'lvr': '',
                'valuation': '',
                'pricing': '',
                'offset': '',
                'loan_detail_address': '',
            }
            
            loan_detail_data = serializer.validated_data.get('loan_details', default_loan_detail)

            # Use update method to ensure all keys exist, filled with data if present or empty strings if not
            default_loan_detail.update(loan_detail_data)
            
            default_fund_detail = {
                'loan_amount': 0,
                'cash_out_amount': 0,
                'stamp_duty': 0
            }
            
            fund_detail_data = serializer.validated_data.get('fund_detail', default_fund_detail)
            default_fund_detail.update(fund_detail_data)
            
            # Now extract each value, ensuring they are integers or fall back to 0
            loan_amount = int(default_fund_detail['loan_amount']) or 0
            cash_out_amount = int(default_fund_detail['cash_out_amount']) or 0
            stamp_duty = int(default_fund_detail['stamp_duty']) or 0
            
            # Perform the calculation
            funds_required = loan_amount - cash_out_amount + stamp_duty
        
            context = {
                'date': serializer.validated_data.get('date', ""),
                'processor_name': processor_name,
                'processor_email': processor_email,
                'processor_phone': processor_phone,
                'secondary_processor_name': secondary_processor_name,
                'secondary_processor_email': secondary_processor_email,
                'secondary_processor_phone': secondary_processor_phone,
                'applicant_first_name': frist_name,
                'applicant_last_last': last_name,
                'applicant_occupation': primary_contact_occupation,
                'applicant_citizenship': primary_contact_citizenship,
                'applicant_residency': primary_contact_residency,
                'applicant_employer': primary_contact_employer,
                'co_applicant_status': serializer.validated_data.get('co_applicant_status', False),
                
                'applicant_2_first_name': frist_name_2,
                'applicant_2_last_last': last_name_2,
                'applicant_2_occupation': secondary_contact_occupation,
                'applicant_2_citizenship': secondary_contact_citizenship,
                'applicant_2_residency': secondary_contact_residency,
                'applicant_2_employer': secondary_contact_employer,
                
                'loan_detail': default_loan_detail,
                'fund_detail': default_fund_detail,
                'funds_required': funds_required,
                'generated_loan_purpose': serializer.validated_data.get('generated_loan_purpose', ""),
                'generated_applicant_overview': serializer.validated_data.get('generated_applicant_overview', ""),
                'generated_living_condition': serializer.validated_data.get('generated_living_condition', ""),
                'generated_employment_income': serializer.validated_data.get('generated_employment_income', ""),
                'generated_commitments': serializer.validated_data.get('generated_commitments', ""),
                'generated_others': serializer.validated_data.get('generated_others', ""),
                'generated_mitigants': serializer.validated_data.get('generated_mitigants', ""),
            }
 
            html_content = render_to_string('pdf_template.html', context)
            # pdf_content = html_to_pdf2("pdf_template.html", context)
            # if pdf_content is None:
            #     return Response("Invalid PDF", status=status.HTTP_400_BAD_REQUEST)
            
             # Generate the PDF
            pdf = html_to_pdf(html_content)

            # Return the PDF as an HttpResponse
            response = HttpResponse(pdf, content_type='application/pdf')
            response['Content-Disposition'] = 'inline; filename="document.pdf"'
            
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
            
class BrokerNoteListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        try:
            notes_query =  Note.objects.filter(created_by=request.user, status='active').order_by('-updated_at')
            
            if request.query_params.get('latest') == 'true':
                notes_query = notes_query[:3]  # Limit to latest 3 notes
            serializer = BrokerNoteSerializer(notes_query, many=True)
            response_data = {
                "success": True,
                "statusCode": status.HTTP_200_OK,
                "data": serializer.data,
            }
            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 
    
    def post(self, request, *args, **kwargs):
        serializer = BrokerNoteSerializer(data=request.data)
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
                loan_details = serializer.validated_data.get('loan_details', {})
                updated_json_data = opportunity.json_data
                opportunity_payload = {
                    'lender': loan_details.get('lender'),
                    'loanTerm': loan_details.get('loan_term'),
                    'propertyValue':loan_details.get('property_value'),
                    'interestRate': loan_details.get('interest_rate'),
                    "purpose": loan_details.get('loan_purpose'),
                    'loanAmount' : loan_details.get('loan_amount'),
                    'product': loan_details.get('product'),
                    'lvr': loan_details.get('lvr'),
                    'valuation': loan_details.get('valuation'),
                    'pricing': loan_details.get('pricing'),
                    'offset': loan_details.get('offset'),
                    'cashOutReason': loan_details.get('cash_out_reason'),
                }
                updated_json_data.update(opportunity_payload)
                opportunity.json_data = updated_json_data
                opportunity.save()
                
                note = Note(
                    loan_details=loan_details,
                    funds_available=serializer.validated_data.get('funds_available', {}),
                    funds_complete=serializer.validated_data.get('funds_complete', {}),
                    loan_purpose_note=serializer.validated_data.get('loan_purpose_note'),
                    applicant_overview_note=serializer.validated_data.get('applicant_overview_note'),
                    living_condition_note=serializer.validated_data.get('living_condition_note'),
                    employment_income_note=serializer.validated_data.get('employment_income_note'),
                    commitments_note=serializer.validated_data.get('commitments_note'),
                    other_note=serializer.validated_data.get('other_note'),
                    mitigants_note=serializer.validated_data.get('mitigants_note'),
                    opportunity=opportunity,
                    created_by=request.user,  # Assuming the user is authenticated
                    updated_by=request.user
                )
                note.save()
                response_data = {
                    "success": True,
                    "statusCode": status.HTTP_201_CREATED,
                    "data": BrokerNoteSerializer(note).data
                }

                return Response(response_data, status=status.HTTP_201_CREATED)
                
        except ValidationError as e:  # Specific exceptions can be more useful
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class BrokerNoteDetailUpdateDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk, *args, **kwargs):
        try:
            note = Note.objects.filter(id=pk, created_by=request.user, status='active').first()
            if not note:
                return Response({
                    "error": {
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "message": "Note with the given id does not exist or is not active",
                    }
                }, status=status.HTTP_404_NOT_FOUND)
            serializer = BrokerNoteSerializer(note)
            response_data = {
                "success": True,
                "statusCode": status.HTTP_200_OK,
                "data": serializer.data,
            }
            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def delete(self, request, pk, *args, **kwargs):
        note = Note.objects.get(pk=pk)
        if not note:
            return Response({"error": "Broker note not found."}, status=status.HTTP_404_NOT_FOUND)
        if request.user != note.created_by:
            return Response({"error": "You don't have permission to delete this Broker Note."}, status=status.HTTP_403_FORBIDDEN)
        
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
            return Response({"error": "Broker note not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = BrokerNoteSerializer(note, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        if request.user != note.created_by:
            return Response({"error": "You don't have permission to update this broker Note."}, status=status.HTTP_403_FORBIDDEN)
        
        try:
            with transaction.atomic():
                loan_details = serializer.validated_data.get('loan_details', {})
                opportunity = note.opportunity
                updated_json_data = opportunity.json_data
                opportunity_payload = {
                    'lender': loan_details.get('lender'),
                    'loanTerm': loan_details.get('loan_term'),
                    'propertyValue':loan_details.get('property_value'),
                    'interestRate': loan_details.get('interest_rate'),
                    "purpose": loan_details.get('loan_purpose'),
                    'loanAmount' : loan_details.get('loan_amount'),
                    'product': loan_details.get('product'),
                    'lvr': loan_details.get('lvr'),
                    'valuation': loan_details.get('valuation'),
                    'pricing': loan_details.get('pricing'),
                    'offset': loan_details.get('offset'),
                    'cashOutReason': loan_details.get('cash_out_reason'),
                }
                updated_json_data.update(opportunity_payload)
                opportunity.json_data = updated_json_data
                opportunity.save()
                
                note.updated_by = request.user
                note.loan_details=loan_details
                note.funds_available=serializer.validated_data.get('funds_available', {})
                note.funds_complete=serializer.validated_data.get('funds_complete', {})
                note.loan_purpose_note=serializer.validated_data.get('loan_purpose_note')
                note.applicant_overview_note=serializer.validated_data.get('applicant_overview_note')
                note.living_condition_note=serializer.validated_data.get('living_condition_note')
                note.employment_income_note=serializer.validated_data.get('employment_income_note')
                note.commitments_note=serializer.validated_data.get('commitments_note')
                note.other_note=serializer.validated_data.get('other_note')
                note.mitigants_note=serializer.validated_data.get('mitigants_note')
                
                note.save()
                
                serializer_data = BrokerNoteSerializer(note)
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

class SystemPromptListAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            system_prompts = BrokerNoteSystemprompt.objects.all()
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
            prompt_instance = BrokerNoteSystemprompt.objects.get(pk=pk)
        except BrokerNoteSystemprompt.DoesNotExist:
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