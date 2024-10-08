from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import BankPolicy, Policy, Bank, ChatSession, Message
from .serializers import BankPolicyNoteSerializer, BankPolicySerializer, BankPolicyQuerySerializer, BankSerializer, PolicySerializer, ChatSessionSerializer, MessageSerializer
from django.db.models import Prefetch
import requests
import os
from requests.exceptions import RequestException
# Create your views here.

class BankListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            banks = Bank.objects.all()
            serializer = BankSerializer(banks, many=True)
            response_data = {
                "success": True,
                "statusCode": status.HTTP_200_OK,
                "data": serializer.data,
            }
            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 
        
class PolicyListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            policies = Policy.objects.all()
            serializer = PolicySerializer(policies, many=True)
            response_data = {
                "success": True,
                "statusCode": status.HTTP_200_OK,
                "data": serializer.data,
            }
            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 
        
            
class BankPolicyListAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        # Fetch all policies and prefetch related bank policies and their banks
        policies = Policy.objects.prefetch_related(
            Prefetch('bank_policies', queryset=BankPolicy.objects.select_related('bank'))
        ).all()

        # Initialize the set for unique banks
        banks_set = set()
        # Initialize the data structure for the response
        data = []

        # Iterate over each policy
        for policy in policies:
            policy_data = {
                "policy_id": policy.id,  # Include the policy ID
                "policy_name": policy.name
            }
            # Iterate over each bank policy related to the policy
            for bank_policy in policy.bank_policies.all():
                banks_set.add((bank_policy.bank.id, bank_policy.bank.name))  # Collect bank IDs and names
                # Structure the bank-specific data including IDs
                policy_data[f"bank_{bank_policy.bank.id}"] = {
                    "description": bank_policy.description or "No description available",
                    "bank_policy_id": bank_policy.id,  # Include the bank policy ID for updates
                    "bank_name": bank_policy.bank.name
                    
                }

            data.append(policy_data)

        # Create bank objects from the set of tuples
        banks_list = [{"id": bank_id, "name": bank_name} for bank_id, bank_name in sorted(banks_set, key=lambda x: x[1])]

        # Ensure all policies have all bank columns, even if there's no existing bank policy link
        for policy in data:
            for bank in banks_list:
                bank_key = f"bank_{bank['id']}"
                if bank_key not in policy:
                    policy[bank_key] = {"description": "No data", "bank_policy_id": None}
        response_data = {
                "success": True,
                "statusCode": status.HTTP_200_OK,
                "data": {"banks": banks_list, "policies": data},
            }
        return Response(response_data, status=status.HTTP_200_OK)

class BankPolicyDetailUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    
class BankPolicyNoteAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        serializer = BankPolicyQuerySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        bank_id = serializer.validated_data.get('bank_id')
        policy_id = serializer.validated_data.get('policy_id')
        user_query = serializer.validated_data.get('user_query')
        if 'chat_id' in serializer.validated_data:
            chat_session = ChatSession.objects.get(id=serializer.validated_data['chat_id'])
        else:
            chat_session = ChatSession.objects.create(user=request.user, title=user_query)
        Message.objects.create(chat_session=chat_session, text=user_query, sender='user')    
           
        if bank_id and policy_id:
                queryset = BankPolicy.objects.filter(bank_id=bank_id, policy_id=policy_id)
        elif bank_id:
            queryset = BankPolicy.objects.filter(bank_id=bank_id)
        elif policy_id:
            queryset = BankPolicy.objects.filter(policy_id=policy_id)
        result_serializer = BankPolicyNoteSerializer(queryset, many=True)   
    
        gpt_response = get_gpt_response(user_query, result_serializer.data)
        if 'choices' in gpt_response and gpt_response['choices']:
            assistant_response = gpt_response['choices'][0]['message']['content']
            Message.objects.create(chat_session=chat_session, text=assistant_response, sender='assistant')
            
        response_data = {
                "success": True,
                "statusCode": status.HTTP_200_OK,
                "data": gpt_response,
                "chat_id": chat_session.id
            }
        return Response(response_data, status=status.HTTP_200_OK)

def get_gpt_response(user_query, policy_data):
    
    context = "\n\n".join([
        f"Policy Name: {item['policy']['name']}, Description: {item['description']}" 
        for item in policy_data
    ])
    system_message = f"I am a knowledgeable assistant trained to provide information based on detailed policy data."
    bearer_token = os.getenv('OPEN_AI_KEY')
    temperature = float(os.getenv('OPEN_AI_TEMPERATURE'))
    OPEN_AI_URL = os.getenv('OPEN_AI_URL')
    GPT_MODEL = os.getenv('GPT_LATEST_MODEL')
    
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
                "content": system_message
            },
            {
                "role": "user",
                "content": user_query
            },
             {"role": "assistant", "content": context}
        ],
        "temperature":temperature
    }

    # The endpoint URL
    url = OPEN_AI_URL

    # Make the POST request
    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        return response.json()  # Return JSON response data
    except RequestException as e:
        return {'error': str(e)}  # Return error details as JSON
    
    

class ChatSessionListAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            chat_sessions = ChatSession.objects.filter(user=request.user)
            serializer = ChatSessionSerializer(chat_sessions, many=True)
            response_data = {
                "success": True,
                "statusCode": status.HTTP_200_OK,
                "data": serializer.data,
            }
            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 

class MessageListAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, session_id):
        try:
            messages = Message.objects.filter(chat_session_id=session_id)
            serializer = MessageSerializer(messages, many=True)
            response_data = {
                "success": True,
                "statusCode": status.HTTP_200_OK,
                "data": serializer.data,
            }
            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 
        
        
        