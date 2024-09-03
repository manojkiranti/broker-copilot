from django.db import models
from enum import Enum
from django.contrib.auth import get_user_model
from opportunity_app.models import Opportunity, LenderChoices
from utils.constant import StatusChoices
User = get_user_model()

# Create your models here.
class SystemPrompt(models.Model):
    loan_objectives = models.TextField(blank=True, null=True)
    loan_requirements = models.TextField(blank=True, null=True)
    loan_circumstances = models.TextField(blank=True, null=True)
    loan_financial_awareness = models.TextField(blank=True, null=True)
    loan_prioritised = models.TextField(blank=True, null=True)
    lender_loan = models.TextField(blank=True, null=True)
    loan_structure = models.TextField(blank=True, null=True)
    goals_objectives = models.TextField(blank=True, null=True)
    def __str__(self):
        return f"Compliance Note Systemprompt"

class CompliancePromptChoices(models.TextChoices):
    LOAN_OBJECTIVES = 'loan_objectives', 'Loan Objectives'
    LOAN_REQUIREMENTS = 'loan_requirements', 'Loan Requirements'
    LOAN_CIRCUMSTANCES = 'loan_circumstances', 'Loan Circumstances'
    LOAN_FINANCIAL_AWARENESS = 'loan_financial_awareness', 'Loan Financial Awareness'
    LOAN_PRIORITISED = 'loan_prioritised', 'Loan Prioritised'
    LENDER_LOAN = 'lender_loan', 'Lender Loan'
    LOAN_STRUCTURE = 'loan_structure', 'Loan Structure'
    GOALS_OBJECTIVES = 'goals_objectives', 'Goals Objectives'
  

class ComplianceSystemPrompt(models.Model):
    prompt_type = models.CharField(choices=CompliancePromptChoices.choices)
    prompt =  models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=StatusChoices.choices, default=StatusChoices.ACTIVE)   
    
    created_by = models.ForeignKey(User, related_name='created_system_prompt', on_delete=models.SET_NULL, null=True)
    updated_by = models.ForeignKey(User, related_name='updated_system_prompt', on_delete=models.SET_NULL, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.prompt_type
    
class Note(models.Model):
    class ComplianceNoteStatus(models.TextChoices):
        ACTIVE  = 'active', 'Active',
        INACTIVE = 'inactive', 'Inactive'
    
    class OffsetChoices(models.TextChoices):
        YES = 'yes', 'Yes'
        NO = 'no', 'No'
        
    class DocumentIdentificationChoices(models.TextChoices):
        FACE_TO_FACE = 'face_to_face', 'Face to Face'
        CERTIFIED_PERSONS = 'certified_persons', 'Certified Persons'
        BRANCH = 'branch', 'Branch'
        VIDEO_OVER_INTERNET = 'video_over_internet', 'Video over Internet'
    
    class ClientInterviewChoices(models.TextChoices):
        FACE_TO_FACE = 'face_to_face', 'Face to Face'
        VIDEO = 'video', 'Video'
        TELEPHONE = 'telephone', 'Telephone'
        EMAIL = 'email', 'Email'
    
    class RateTypeChoices(models.TextChoices):
        FIXED_RATE = 'fixed_rate', 'Fixed Rate'
        VARIABLE_RATE = 'variable_rate', 'Variable Rate'
        FIXED_AND_VARIABLE_RATE = 'fixed_and_variable_rate', 'Fixed & Variable Rate'
        
    class RepaymentChoices(models.TextChoices):
        INTEREST_ONLY = 'interest_only', 'Interest Only'
        PL_REPAYMENTS = 'p_and_l_repayments', 'P&L Repayments'
        
    class FrequencyChoices(models.TextChoices):
        MONTHLY = 'monthly', 'Monthly'
        FORTNIGHTLY = 'fortnightly', 'Fortnightly'
        WEEKLY = 'weekly', 'Weekly'
    
    class CashOutInvolvedChoices(models.TextChoices):
        ASSIST_WITH_PROPERTY_PURCHASE = 'assist_with_the_property_purchase_transaction', 'Assist with the property purchase transaction'
        NON_STRUCTURAL_RENOVATION = 'non_structural_renovation_of_existing_properties', 'Non-structural renovation of existing properties'
        CASH_BUY_FUTURE_PROPERTY = 'to_cash_buy_future_australian_property_outright', 'To cash buy future Australian property outright'
    
    class LoanStructureChoices(models.TextChoices):
        STANDALONE = 'standalone', 'Standalone'
        CROSS_COLLATERALISED = 'cross_collateralised', 'Cross-Collateralised'
        MULTIPLE_SECURITIES = 'multiple_securities', 'Multiple Securities'
    
    document_identification_method = models.CharField(max_length=50, choices=DocumentIdentificationChoices.choices, null=True, blank=True)
    client_interview_method = models.CharField(max_length=50, choices=ClientInterviewChoices.choices, null=True, blank=True )
    
    credit_guide_provided = models.DateTimeField(null=True, blank=True)
    estimated_settlement_date = models.DateTimeField(null=True, blank=True)
    facility_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    rate_type = models.CharField(max_length=50, choices=RateTypeChoices.choices, null=True, blank=True )
    repayment_type = models.CharField(max_length=50, choices=RepaymentChoices.choices, null=True, blank=True )
    repayment_frequency = models.CharField(max_length=50, choices=FrequencyChoices.choices, null=True, blank=True )
    offset = models.CharField(max_length=3,choices=OffsetChoices.choices,null=True,blank=True)
    
    cash_out_involved = models.CharField(max_length=100, choices=CashOutInvolvedChoices.choices, null=True, blank=True )
    loan_structure = models.CharField(max_length=100, choices=LoanStructureChoices.choices, null=True, blank=True )
    
    loan_scenario_lender_1 = models.CharField(max_length=100, choices=LenderChoices.choices, null=True, blank=True )
    loan_scenario_lender_2 = models.CharField(max_length=100, choices=LenderChoices.choices, null=True, blank=True )
    loan_scenario_lender_3 = models.CharField(max_length=100, choices=LenderChoices.choices, null=True, blank=True )
    
    loan_objective_note = models.TextField(blank=True, null=True)
    loan_requirement_note = models.TextField(blank=True, null=True)
    loan_circumstances_note = models.TextField(blank=True, null=True)
    loan_financial_awareness_note = models.TextField(blank=True, null=True)
    loan_structure_note = models.TextField(blank=True, null=True)
    loan_prioritised_note = models.TextField(blank=True, null=True)
    lender_loan_note = models.TextField(blank=True,null=True)
    
    status = models.CharField(max_length=20, choices=ComplianceNoteStatus.choices, default=ComplianceNoteStatus.ACTIVE)
    
    opportunity = models.ForeignKey(Opportunity, on_delete=models.CASCADE, null=True, related_name="compliance_opportunities")
    
    created_by = models.ForeignKey(User, related_name='created_compliance_note', on_delete=models.SET_NULL, null=True)
    updated_by = models.ForeignKey(User, related_name='updated_compliance_note', on_delete=models.SET_NULL, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    @staticmethod
    def get_document_identification_choices():
        return [
            {'value': choice.value, 'label': choice.label}
            for choice in Note.DocumentIdentificationChoices
        ]
    def __str__(self):
        return self.opportunity.name