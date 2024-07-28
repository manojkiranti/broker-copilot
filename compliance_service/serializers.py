from rest_framework import serializers

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
    