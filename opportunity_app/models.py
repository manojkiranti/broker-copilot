from django.db import models
from django.db.models import Q
from enum import Enum
from django.contrib.auth import get_user_model

User = get_user_model()


class Stage(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name
    
class LenderChoices(models.TextChoices):
    AAA_FINANCE = 'aaa_finance', 'AAA Finance'
    ANZ_BANK = 'anz_bank', 'ANZ Bank'
    BOQ = 'boq', 'BOQ'
    CBA = 'cba', 'CBA'
    HERITAGE = 'heritage', 'Heritage'
    ST_GEORGE_BANK = 'st_george_bank', 'St. George Bank'
    MACQUARIE_BANK = 'macquarie_bank', 'Macquarie Bank'
    HSBC = 'hsbc', 'HSBC'
    HSBC_AU = 'hsbc_au', 'HSBC AU'
    NAB = 'nab', 'NAB'
    SUNCORP = 'suncorp', 'Suncorp'
    WESTPAC = 'westpac', 'Westpac'
    BC_INVEST = 'bc_invest', 'BC Invest'
    BRIGHTEN = 'brighten', 'Brighten'
    LA_TROBE = 'la_trobe', 'LaTrobe'
    MEZY = 'mezy', 'MEZY'
    MA_MONEY = 'ma_money', 'MA Money',
    BANKWEST = 'bankwest', 'Bankwest',
    ING = 'ing', 'Ing',
    GREAT_SOUTHERN_BANK = 'great_southern_bank', 'Great Southern Bank'
    
class LoanPurposeChoices(models.TextChoices):
    INVESTMENT_PROPERTY = 'investment_property', 'Investment Property'
    INVESTMENT_PROPERTY_PURCHASE = 'investment_property_purchase', 'Investment Property Purchase'
    INVESTMENT_PROPERTY_PRE_APPROVAL = 'investment_property_pre_approval', 'Investment Property Pre-approval'
    INVESTMENT_PROPERTY_REFINANCE = 'investment_property_refinance', 'Investment Property Refinance'
    INVESTMENT_PROPERTY_REFINANCE_CASHOUT = 'investment_property_refinance_cashout', 'Investment Property Refinance + Cashout'
    INVESTMENT_PROPERTY_CASHOUT_ONLY = 'investment_property_cashoutonly', 'Investment Property Cashout Only'
    INVESTMENT_VACANT_LAND = 'investment_vacant_land', 'Investment Vacant Land'
    INVESTMENT_HOUSE_AND_LAND_CONSTRUCTION = 'investment_house_and_land_construction', 'Investment House & Land Construction'
    OWNER_OCCUPIER_PROPERTY_PURCHASE = 'owner_occupier_property_purchase', 'Owner-occupier Property Purchase'
    INV_INITIALLY_THEN_OO = 'inv_initially_then_oo', 'INV initially, then OO'
    HOLIDAY_HOME = 'holiday_home', 'Holiday Home'
    OWNER_OCCUPIER_PROPERTY_PRE_APPROVAL = 'owner_occupier_property_pre_approval', 'Owner-occupier Property Pre-approval'
    OWNER_OCCUPIER_PROPERTY_REFINANCE = 'owner_occupier_property_refinance', 'Owner-occupier Property Refinance'
    OWNER_OCCUPIER_PROPERTY_REFINANCE_EQUITY_RELEASE = 'owner_occupier_property_refinance_equity_release', 'Owner-occupier Property Refinance + Equity Release'
    OWNER_OCCUPIER_PROPERTY_EQUITY_CASH_OUT = 'owner_occupier_property_equity_cash_out', 'Owner-occupier Property Equity Cash-out'
    OWNER_OCCUPIER_VACANT_LAND = 'owner_occupier_vacant_land', 'Owner-occupier Vacant Land'
    OWNER_OCCUPIER_HOUSE_AND_LAND_CONSTRUCTION = 'owner_occupier_house_and_land_construction', 'Owner-Occupier House & Land Construction'
        
class ContactsOpportunity(models.Model):
    class OpportunityStatus(models.TextChoices):
        ACTIVE  = 'active', 'Active',
        INACTIVE = 'inactive', 'Inactive'
    
        
    name = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=25, null=True, blank=True)
    citizenship = models.CharField(max_length=100, null=True, blank=True)
    residency = models.CharField(max_length=99, null=True, blank=True)
    country_code = models.CharField(max_length=20, null=True, blank=True)
    website_field_id = models.CharField(max_length=50, null=True, blank=True)
    website_form_id = models.CharField(max_length=20, null=True, blank=True)
    website_date_updated = models.DateTimeField(null=True, blank=True)
    
    status = models.CharField(max_length=20, choices=OpportunityStatus.choices, default=OpportunityStatus.ACTIVE)
    
    created_by = models.ForeignKey(User, related_name='created_contacts', on_delete=models.SET_NULL, null=True)
    updated_by = models.ForeignKey(User, related_name='updated_contacts', on_delete=models.SET_NULL, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.email
    
class Opportunity(models.Model):
    class OpportunityType(models.TextChoices):
        PURCHASE = 'purchase', 'Purchase'
        REFINANCE = 'refinance', 'Refinance'

    class OpportunityStatus(models.TextChoices):
        ACTIVE = 'active', 'Active'
        INACTIVE = 'inactive', 'Inactive'

        
    name = models.CharField(max_length=255, unique=True)
    type = models.CharField(max_length=20, choices=OpportunityType.choices)
    status = models.CharField(max_length=20, choices=OpportunityStatus.choices, default=OpportunityStatus.ACTIVE)
    stage = models.ForeignKey(Stage, on_delete=models.SET_NULL, null=True, blank=True, related_name='opportunities')
    
    website_tracking_id = models.CharField(unique=True, max_length=255, null=True)
    json_data = models.JSONField(default=dict)

    primary_contact = models.ForeignKey(ContactsOpportunity, on_delete=models.SET_NULL, null=True, related_name="primary_opportunities")
    secondary_contact = models.ForeignKey(ContactsOpportunity, on_delete=models.SET_NULL, null=True,  blank=True, related_name="secondary_opportunities")
    other_contact = models.ForeignKey(ContactsOpportunity, on_delete=models.SET_NULL, null=True, blank=True, related_name="other_opportunities")
   
    primary_processor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="primary_processor_opportunity")
    secondary_processor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,related_name="secondary_processor_opportunity")
    
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="created_opportunity")
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="updated_opportunity")
    
    start_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.status} - {self.name}"

