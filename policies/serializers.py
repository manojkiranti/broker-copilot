from rest_framework import serializers
from .models import Bank, Policy, BankPolicy, SenderChoices

class BankSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bank
        fields = ('id', 'name', 'operating_country')

class PolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = Policy
        fields = ('id', 'name')

class BankPolicySerializer(serializers.Serializer):
    bank_id = serializers.IntegerField()
    policy_id = serializers.IntegerField()
    description = serializers.CharField(max_length=255, allow_null=True, required=False)
    
class BankPolicyNoteSerializer(serializers.ModelSerializer):
    bank = BankSerializer(read_only=True)
    policy = PolicySerializer(read_only=True)
    created_by = serializers.StringRelatedField()
    updated_by = serializers.StringRelatedField()
    
    class Meta:
        model = BankPolicy
        fields = ['id', 'bank', 'policy', 'description', 'created_by', 'updated_by', 'created_at', 'updated_at']

class BankPolicyQuerySerializer(serializers.Serializer):
    bank_id = serializers.IntegerField(required=False, allow_null=True)
    policy_id = serializers.IntegerField(required=False, allow_null=True)
    user_query =  serializers.CharField(max_length=255)
    chat_id = serializers.CharField(max_length=100, allow_null=True, required=False)
    def validate(self, data):
        bank_id = data.get('bank_id')
        policy_id = data.get('policy_id')
        if bank_id is None and policy_id is None:
            raise serializers.ValidationError("Either 'bank_id' or 'policy_id' must be provided.")
        return data

class ChatSessionSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    title = serializers.CharField(read_only=True)
    
class MessageSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    chat_session_id = serializers.IntegerField(source='chat_session.id', read_only=True)
    text = serializers.CharField()
    sender = serializers.ChoiceField(choices=SenderChoices.choices)
    created_at = serializers.DateTimeField(read_only=True)

