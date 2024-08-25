from rest_framework import serializers
from opportunity_app.models import LenderChoices, LoanPurposeChoices
from opportunity_app.serializers import OpportunityNameSerializer, OpportunitySerializer
from .models import Note

class UserContentSerializer(serializers.Serializer):
    user_content = serializers.CharField(max_length=1024, required=False, allow_blank=True)
    compliance_field = serializers.ChoiceField(
        choices=[
            ('loan_objectives', 'Loan Objectives'),
            ('loan_requirements', 'Loan Requirements'),
            ('loan_circumstances', 'Loan Circumstances'),
            ('loan_financial_awareness', 'Loan Financial Awareness'),
            ('loan_prioritised', 'Loan Prioritized'),
            ('lender_loan', 'Lender Loan'),
            ('loan_structure', 'Loan Structure'),
            ('goals_objectives', 'Goals Objectives'),
        ],
        required=True
    )

class ComplianceOpportunitySerializer(serializers.Serializer):
    lvr = serializers.CharField(max_length=10, required=False, allow_null=True, allow_blank=True)
    purpose = serializers.ChoiceField(choices=LoanPurposeChoices.choices, required=False, allow_blank=True, allow_null=True)
    
    
class ComplianceNoteSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    opportunity_id = serializers.IntegerField()
    opportunity = OpportunitySerializer(read_only=True)
    
    document_identification_method = serializers.ChoiceField(choices=Note.DocumentIdentificationChoices, allow_null=True, required=False)
    client_interview_method = serializers.ChoiceField(choices=Note.ClientInterviewChoices.choices, allow_null=True, required=False)
    
    credit_guide_provided = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, allow_null=True)
    estimated_settlement_date = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, allow_null=True)
    facility_amount = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, allow_null=True)
    
    rate_type = serializers.ChoiceField(choices=Note.RateTypeChoices.choices, allow_null=True, required=False)
    repayment_type = serializers.ChoiceField(choices=Note.RepaymentChoices.choices, allow_null=True, required=False)
    repayment_frequency = serializers.ChoiceField(choices=Note.FrequencyChoices.choices, allow_null=True, required=False)
    offset = serializers.ChoiceField(choices=Note.OffsetChoices.choices, required=False, allow_blank=True, allow_null=True)
    
    cash_out_involved = serializers.ChoiceField(choices=Note.CashOutInvolvedChoices.choices, required=False, allow_blank=True, allow_null=True)
    
    loan_structure = serializers.ChoiceField(choices=Note.LoanStructureChoices.choices, required=False, allow_blank=True, allow_null=True)
    
    loan_scenario_lender_1 = serializers.ChoiceField(choices=LenderChoices.choices, required=False, allow_blank=True, allow_null=True)
    loan_scenario_lender_2 = serializers.ChoiceField(choices=LenderChoices.choices, required=False, allow_blank=True, allow_null=True)
    loan_scenario_lender_3 = serializers.ChoiceField(choices=LenderChoices.choices, required=False, allow_blank=True, allow_null=True)
    
    loan_objective_note = serializers.CharField(style={'base_template': 'textarea.html'}, required=False, allow_blank=True)
    loan_requirement_note = serializers.CharField(style={'base_template': 'textarea.html'}, required=False, allow_blank=True)
    loan_circumstances_note = serializers.CharField(style={'base_template': 'textarea.html'}, required=False, allow_blank=True)
    loan_financial_awareness_note = serializers.CharField(style={'base_template': 'textarea.html'}, required=False, allow_blank=True)
    loan_structure_note = serializers.CharField(style={'base_template': 'textarea.html'}, required=False, allow_blank=True)
    loan_prioritised_note = serializers.CharField(style={'base_template': 'textarea.html'}, required=False, allow_blank=True)
    lender_loan_note = serializers.CharField(style={'base_template': 'textarea.html'}, required=False, allow_blank=True)
    
    opportunity_data = ComplianceOpportunitySerializer(required=False)
    
    updated_at = serializers.DateTimeField(read_only=True)
    