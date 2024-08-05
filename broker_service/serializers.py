from rest_framework import serializers

class UserContentSerializer(serializers.Serializer):
    user_content = serializers.CharField(max_length=5000, required=False, allow_blank=True)
    broker_note_field = serializers.ChoiceField(
        choices=[
            ('loan_purpose', 'Loan Purpose'),
            ('applicant_overview', 'Applicant Overview'),
            ('living_condition', 'Living Condition'),
            ('employment_income', 'Employment Income'),
            ('commitments', 'Commitments'),
            ('others', 'Others'),
            ('mitigants', 'Mitigants')
        ],
        required=True
    )