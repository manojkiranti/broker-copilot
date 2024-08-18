from rest_framework import serializers

from opportunity_app.serializers import ContactDataSerializer

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

class ContactSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100, allow_null=True, allow_blank=True, required=False)
    email = serializers.EmailField(allow_blank=True, allow_null=True, required=False)
    phone = serializers.CharField(max_length=20, allow_blank=True, required=False)

class NoteContactDataSerializer(ContactDataSerializer):
    occupation = serializers.CharField(max_length=100, allow_null=True, allow_blank=True, required=False)
    employer = serializers.CharField(max_length=100, allow_null=True, allow_blank=True, required=False)
    email = serializers.EmailField(allow_blank=True, allow_null=True, required=False) 
    def to_representation(self, instance):
        # Exclude country_code from the serialized output
        ret = super().to_representation(instance)
        ret.pop('country_code', None)
        return ret

class LoanDetailSerializer(serializers.Serializer):
    finance_due_date = serializers.CharField(max_length=20, allow_null=True, allow_blank=True, required=False)
    settlement_date = serializers.CharField(max_length=20, allow_null=True, allow_blank=True, required=False)
    lender = serializers.CharField(max_length=100, allow_null=True, allow_blank=True, required=False)
    loan_term = serializers.IntegerField(max_value=20, allow_null=True, required=False)
    property_value = serializers.IntegerField(allow_null=True, required=False)
    interest_rate = serializers.IntegerField(max_value=12, allow_null=True, required=False)
    loan_purpose = serializers.CharField(max_length=100, allow_null=True,allow_blank=True, required=False)
    loan_amount = serializers.IntegerField(allow_null=True, required=False)
    product = serializers.CharField(max_length=100, allow_null=True, allow_blank=True, required=False)
    lvr = serializers.IntegerField(allow_null=True, required=False)
    valuation = serializers.CharField(max_length=100,  allow_null=True, allow_blank=True, required=False)
    pricing = serializers.CharField(max_length=100,  allow_null=True, allow_blank=True, required=False)
    offset = serializers.CharField(max_length=10,  allow_null=True, allow_blank=True, required=False)
    loan_detail_address = serializers.CharField(max_length=100,  allow_null=True, allow_blank=True, required=False)

class FundsDetailSerializer(serializers.Serializer):
    loan_amount = serializers.IntegerField(allow_null=True, required=False)
    cash_out_amount = serializers.IntegerField( allow_null=True, required=False)
    stamp_duty = serializers.IntegerField(max_value=10000, allow_null=True, required=False)
    
class GenerateBrokerNotePdfSerializer(serializers.Serializer):
    date = serializers.CharField(max_length=10, allow_null=True, allow_blank=True, required=False)
    processor = ContactSerializer(required=False)
    primary_contact = NoteContactDataSerializer(required=False)
    co_applicant_status = serializers.BooleanField()
    secondary_contact = NoteContactDataSerializer(required=False)
    loan_detail = LoanDetailSerializer()
    fund_detail = FundsDetailSerializer()
    generated_loan_purpose = serializers.CharField(allow_blank=True, allow_null=True, required=False, style={'base_template': 'textarea.html'})
    generated_applicant_overview = serializers.CharField(allow_blank=True, allow_null=True, required=False, style={'base_template': 'textarea.html'})
    generated_living_condition = serializers.CharField(allow_blank=True, allow_null=True, required=False, style={'base_template': 'textarea.html'})
    generated_employment_income = serializers.CharField(allow_blank=True, allow_null=True, required=False, style={'base_template': 'textarea.html'})
    generated_commitments = serializers.CharField(allow_blank=True, allow_null=True, required=False, style={'base_template': 'textarea.html'})
    generated_others = serializers.CharField(allow_blank=True, allow_null=True, required=False, style={'base_template': 'textarea.html'})
    generated_mitigants = serializers.CharField(allow_blank=True, allow_null=True, required=False, style={'base_template': 'textarea.html'})
    
    
    