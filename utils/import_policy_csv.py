import csv
import re
from django.db import transaction
from django.db.utils import IntegrityError
from policies.models import Bank, Policy, BankPolicy
from django.contrib.auth import get_user_model

User = get_user_model()
def clean_policy_name(name):
        # Strip leading/trailing whitespace and normalize spaces
        cleaned_name = re.sub(r'\s+', ' ', name.strip())
        # You can add more cleaning rules here if needed
        return cleaned_name
    
def clean_bank_name(name):
     # Strip leading/trailing whitespace and normalize spaces
    cleaned_name = re.sub(r'\s+', ' ', name.strip())
    # You can add more cleaning rules here if needed
    return cleaned_name

def get_policy_by_name(name):
    try:
        return Policy.objects.get(name=name)
    except Policy.DoesNotExist:
        return None

def get_bank_by_name(name):
    try:
        return Bank.objects.get(name=name)
    except Bank.DoesNotExist:
        return None
    
def import_data(csv_filepath):
    user_creator = User.objects.get(id=1)
    user_updater = User.objects.get(id=1)
    with open(csv_filepath, mode='r', encoding='utf-8-sig') as file:
        reader = csv.DictReader(file)
        policy_name_column = next(iter(reader.fieldnames)) 
        with transaction.atomic():
            
            for row in reader:
                policy_name_raw = row[policy_name_column].strip() 
                policy_name = clean_policy_name(policy_name_raw)
                if policy_name.strip():
                    policy = Policy.objects.get(name=policy_name)
                    for bank_name, policy_detail in row.items():
                        clean_bank = clean_bank_name(bank_name)
                        if(clean_bank != 'Name'):
                            bank = Bank.objects.get(name=clean_bank)
                            BankPolicy.objects.create(
                                bank=bank,
                                policy=policy,
                                description=policy_detail.strip(),
                                created_by=user_creator,
                                updated_by=user_updater
                            )
                            
                        
                        
                # policy = Policy.objects.get(name=policy_name)
                # if not policy:
                #     print(f"Policy not found for name: {policy_name}")
                #     continue
                # for bank_name, policy_detail in row.items():
                #     if  bank_name == policy_name_column or not policy_detail.strip():
                #         continue  
                #     clean_bank = clean_bank_name(bank_name)
                    # bank = Bank.objects.get(name=clean_bank)
                    # if not bank:
                    #     print(f"Bank not found for name: {clean_bank}")
                    #     continue
                   
                    # BankPolicy.objects.create(
                    #     bank=bank,
                    #     policy=policy,
                    #     description=policy_detail.strip(),
                    #     created_by=user_creator,
                    #     updated_by=user_updater
                    # )
           