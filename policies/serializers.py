from rest_framework import serializers
from .models import Bank, Policy, BankPolicy

class BankSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bank
        fields = ('id', 'name', 'operating_country')

class PolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = Policy
        fields = ('id', 'name')

class BankPolicySerializer(serializers.ModelSerializer):
    bank = BankSerializer(read_only=True)
    policy = PolicySerializer(read_only=True)
    created_by = serializers.StringRelatedField()
    updated_by = serializers.StringRelatedField()
    
    class Meta:
        model = BankPolicy
        fields = ['id', 'bank', 'policy', 'description', 'created_by', 'updated_by', 'created_at', 'updated_at']