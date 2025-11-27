# functions.py
# Contains helper functions for Malaysian Tax Input Program

import pandas as pd
import os

# Verify user's credentials by checking IC number format and password
def verify_user( ic_number, password):
    # Check if IC number is exactly 12 digits
    if len(ic_number) != 12 or not ic_number.isdigit():
        return False
    # Check if password matches last 4 digits of IC
    if password == ic_number[-4:]:
        return True
    return False


# Calculate tax payable based on Malaysian tax rates for 2024 
# Chargable income applied to Mlaysian Progressive Tax Rates
# Tax Brackets (Based on LHDN)
def calculate_tax(income, tax_relief):
    chargeable_income = income - tax_relief

    # Bracket A: 0 - 5,000 (Rate 0%)
    if chargeable_income <= 5000:
        return 0.0
    tax_payable = 0.0
    
    # Bracket B: 5,001 - 20,000 (Rate 1%)
    if chargeable_income > 5000:
        taxable_amount = min(chargeable_income, 20000) - 5000
        tax_payable += taxable_amount * 0.01
    
    # Brcket C: 20,001 - 35,000 (Rate 3%)
    if chargeable_income > 20000:
        taxable_amount = min(chargeable_income, 35000) - 20000
        tax_payable += taxable_amount * 0.03
    
    # Bracket D: 35,001 - 50,000 (Rate 6%)
    if chargeable_income > 35000:
        taxable_amount = min(chargeable_income, 50000) - 35000
        tax_payable += taxable_amount * 0.06
    
    # Bracket E: 50,001 - 70,000 (Rate 11%)
    if chargeable_income > 50000:
        taxable_amount = min(chargeable_income, 70000) - 50000
        tax_payable += taxable_amount * 0.11
    
    # Bracket F: 70,001 - 100,000 (Rate 19%)
    if chargeable_income > 70000:
        taxable_amount = min(chargeable_income, 100000) - 70000
        tax_payable += taxable_amount * 0.19
    
    # Brcket G: 100,001 - 400,000 (Rate 25%)
    if chargeable_income > 100000:
        taxable_amount = min(chargeable_income, 400000) - 100000
        tax_payable += taxable_amount * 0.25
    
    # Bracket H: 400,001 - 600,000 (Rate 26%)
    if chargeable_income > 400000:
        taxable_amount = min(chargeable_income, 600000) - 400000
        tax_payable += taxable_amount * 0.26
    
    # Bracket I: 600,001 - 2,000,000 (Rate 28%)
    if chargeable_income > 600000:
        taxable_amount = min(chargeable_income, 2000000) - 600000
        tax_payable += taxable_amount * 0.28
    
    # Bracket J: More  than 2,000,000 (Rate 30%)
    if chargeable_income > 2000000:
        taxable_amount = chargeable_income - 2000000
        tax_payable += taxable_amount * 0.30
    
    return round(tax_payable, 2)


# Individual tax relief amounts
def tax_relief():
    # Prompt user to enter individual tax relief amounts
    print("\n" + "============================================================")
    print("   ENTER YOUR TAX RELIEF DETAILS")
    print("============================================================")
    
    # Define tax relief using a LIST of TUPLES (define name, max amount, name, description)
    relief_types = [
        ('individual_relief', 9000, 'Individual Relief', 'Every Tax Payer Individual will get RM9,000 relief'),
        ('spouse_relief', 4000, 'Spouse Relief', 'Up to RM4,000 for spouse with no/low income'),
        ('medical_relief', 8000, 'Medical Expenses Relief', 'Up to RM8,000 for self, spouse or child'),
        ('lifestyle_relief', 2500, 'Lifestyle Relief', 'Up to RM2,500 for Books, sports, computer, smartphone, internet sub purchase'),
        ('education_relief', 7000, 'Education Fees Relief', 'Up to RM7,000'),
        ('parental_relief', 5000, 'Parental Care Relief', 'Up to RM5,000')]
    
    # Use set to see which reliefs were claimed
    reliefs = {}
    relief_names = set()  
    
    # Process each relief type using LIST OF TUPLES
    for index, (define_name, max_amount, name, description) in enumerate(relief_types, 1):
        print(f"\n{index}. {name} ({description})")
        while True:
            try:
                amount = float(input(f"   Enter amount (0-{max_amount}): RM "))
                if 0 <= amount <= max_amount:
                    reliefs[define_name] = amount
                    if amount > 0:
                        relief_names.add(name)  # Add to SET if claimed
                    break
                print(f"   Error: Amount must be between 0 and {max_amount}")
            except ValueError:
                print("   Error: Please enter a valid number")
    
    # Child relief (special case - based on number of children)
    print("\n7. Child Relief (RM8,000 per child, max 12 children)")
    while True:
        try:
            num_children = int(input("   How many children? (0-12): "))
            if 0 <= num_children <= 12:
                reliefs['child_relief'] = num_children * 8000
                reliefs['num_children'] = num_children
                if num_children > 0:
                    relief_names.add('Child Relief')
                break
            print("   Error: Number must be between 0 and 12")
        except ValueError:
            print("   Error: Please enter a valid number")
    
    # Calculate total relief using a list
    relief_values = [
        reliefs.get('individual_relief', 0),
        reliefs.get('spouse_relief', 0),
        reliefs.get('child_relief', 0),
        reliefs.get('medical_relief', 0),
        reliefs.get('lifestyle_relief', 0),
        reliefs.get('education_relief', 0),
        reliefs.get('parental_relief', 0)]
    reliefs['total_relief'] = sum(relief_values)
    
    # Store the set of claimed relief names 
    reliefs['claimed_reliefs'] = relief_names
    
    # Display summary
    if relief_names:
        print(f"\n You claimed {len(relief_names)} types of relief: {', '.join(sorted(relief_names))}")
    else:
        print("\n No tax reliefs claimed")
    
    return reliefs


# Save user data to CSV file. Creates new file if doesn't exist appends if file exists.
def save_to_csv(data, filename='tax_records.csv', update_existing=False):

    try:
        # Ensure IC number is stored as string (preserve leading zeros)
        if 'ic_number' in data:
            data['ic_number'] = str(data['ic_number'])

        # Create DataFrame from new data
        new_df = pd.DataFrame([data])
        
        # Set ic_number column as string dtype
        new_df['ic_number'] = new_df['ic_number'].astype(str)
        
        # Check if file exists
        try:
            existing_df = pd.read_csv(filename, dtype={'ic_number': str})
            if update_existing and 'id' in data:
                # Update existing record for this user
                user_id = data['id']
                
                # Remove old record for this user
                existing_df = existing_df[existing_df['id'] != user_id]
                
                # Add new record
                combined_df = pd.concat([existing_df, new_df], ignore_index=True)
                combined_df.to_csv(filename, index=False)
                print(f"✓ Updated existing record for user '{user_id}'")
            else:
                # Append new record
                new_df.to_csv(filename, mode='a', header=False, index=False)
                
        except FileNotFoundError:
            # File doesn't exist - create with header
            new_df.to_csv(filename, mode='w', header=True, index=False)
        
        return True
    except Exception as e:
        print(f"Error saving to CSV: {e}")
        return False
    

# Read data from CSV file and return as pandas DataFrame
def read_from_csv(filename='tax_records.csv'):
    try:
        # Try to read the CSV file
        df = pd.read_csv(filename, dtype={'ic_number': str})
        return df
    except FileNotFoundError:
        return None
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return None


# Check if a user ID already exists in the CSV file.
def check_user_exists(user_id, filename='tax_records.csv'):
    df = read_from_csv(filename)

    # checking if the file was read successfully and is not empty
    if df is not None and not df.empty:
        user_data = df[df['id'] == user_id] # look for the user id in the dataframe
        if not user_data.empty:
            # if the user exists return their IC number from the first row found
            # using .iloc[0] to access the first matching row
            # ensure IC number is returned as string with leading zeros preserved
            ic_num = str(user_data.iloc[0]['ic_number']).zfill(12)
            return (True, ic_num)
        
    # Return if file is empty or user not found
    return (False, None)


# Get existing tax record for a user
def get_user_record(user_id, filename='tax_records.csv'):
    df = read_from_csv(filename)
    if df is not None and not df.empty:
        user_data = df[df['id'] == user_id]
        if not user_data.empty:
            # Convert to dictionary and return
            return user_data.iloc[0].to_dict()
    return None

