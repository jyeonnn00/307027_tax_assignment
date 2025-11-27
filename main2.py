# main.py
# handles user registration, authentication, and tax calculation with detailed tax reliefs

from functions2 import (verify_user, calculate_tax, save_to_csv, read_from_csv,
                        check_user_exists, tax_relief, get_user_record)

# main program loop
def main():
    print("\n**************************************************")
    print("  WELCOME TO MALAYSIAN TAX CALCULATOR")
    print("**************************************************")
    
    while True:
        display_menu()
        choice = input("\nEnter your choice (1-4): ").strip()
        if choice == '1':
            register_user()
        elif choice == '2':
            login_user()
        elif choice == '3':
            view_tax_records()
        elif choice == '4':
            print("\nThank you for using Malaysian Tax Calculator!")
            print("Goodbye!\n")
            break
        else:
            print("\nError: Invalid choice! Please enter 1, 2, 3, or 4.")
        
        # pause before showing menu again
        input("\nPress Enter to continue...")


# display the main menu options
def display_menu():
    print("\n" + "==================================================")
    print("   MALAYSIAN TAX CALCULATOR")
    print("--------------------------------------------------")
    print("1. Register and Calculate Tax")
    print("2. Log In")
    print("3. View All Tax Records")
    print("4. Exit")


# register new user 
def register_user():  
    print("\n" + "==================================================")  
    print("--- USER REGISTRATION ---")

    # get user ID
    user_id = input("Enter your User ID: ").strip()
    if not user_id:
        print("User ID cannot be empty!")
        return False
    
    # checking if user already exists using def check_user_exists from functions2
    exists, _ = check_user_exists(user_id)
    if exists:
        print(f"User ID '{user_id}' already exists! Please login instead.")
        return False
    
    # get IC number
    while True:
        ic_number = input("Enter your IC Number: ").strip()
        if len(ic_number) == 12 and ic_number.isdigit():
            break
        else:
            print("IC number must be exactly 12 digits!")
    
    # confirm password match last 4 digits IC number using def verify_user from functions2
    password = input("Enter password (last 4 digits of IC): ").strip()
    if not verify_user(ic_number, password):
        print("Password does not match last 4 digits of IC!")
        return False
    print(f"\n Registration successful for User ID!: {user_id}")
    input("\nPress Enter to continue calculating your tax")

    # after confirm with user info now proceed with tax calculation
    return calculate_and_save_tax(user_id, ic_number, password, is_new_user=True)


# handle user login and tax calculation
def login_user():
    print("\n" + "==================================================")
    print("--- USER LOGIN ---")

    # get user ID and IC number
    user_id = input("Enter your User ID: ").strip()
    
    # Check if user exists using the user ic number
    exists, saved_ic_number = check_user_exists(user_id)
    if not exists:
        print(f"\nUser ID '{user_id}' not found!")
        print("Please register first.")
        return False
    
    # if user exists, verify password
    password = input("Enter password: ").strip()
    if verify_user(saved_ic_number, password):
        print(f"\nWelcome back, {user_id}!")
        # get existing record
        existing_record = get_user_record(user_id)

        if existing_record:
            # display existing data
            display_user_tax_record(existing_record)
            
            # ask if user wants to update
            print("\n" + "============================================================")
            print("1. Update tax calculation (recalculate with new data)")
            print("2. Keep existing record (no changes)")
            
            choice = input("\nEnter 1 or 2: ").strip()
            if choice == '1':
                print("\nProceeding to update your tax calculation...")
                return calculate_and_save_tax(user_id, saved_ic_number, password, is_new_user=False)
            else:
                print("\nKeeping existing record. No changes made.")
                return True
    
    else:
        print("Invalid password!")
        return False


# display a single user's tax record in detail
def display_user_tax_record(record):

    # Format IC number with leading zeros
    ic_formatted = str(record.get('ic_number', '')).zfill(12)
    print("\n" + "============================================================")
    print("YOUR CURRENT TAX RECORD")
    print("--------------------------------------------------")
    print(f"User ID: {record.get('id', 'N/A')}")
    print(f"IC Number: {ic_formatted}")
    print(f"Annual Income: RM {record.get('income', 0):,.2f}")
    
    print(f"\nTax Relief Breakdown:")
    print(f"- Individual: RM {record.get('individual_relief', 0):,.2f}")
    print(f"- Spouse: RM {record.get('spouse_relief', 0):,.2f}")
    print(f"- Child ({int(record.get('num_children', 0))} kids) : RM {record.get('child_relief', 0):,.2f}")
    print(f"- Medical: RM {record.get('medical_relief', 0):,.2f}")
    print(f"- Lifestyle: RM {record.get('lifestyle_relief', 0):,.2f}")
    print(f"- Education: RM {record.get('education_relief', 0):,.2f}")
    print(f"- Parental Care: RM {record.get('parental_relief', 0):,.2f}")
    
    print(f"\nTotal Relief: RM {record.get('total_relief', 0):,.2f}")
    print(f"Chargeable Income: RM {record.get('chargeable_income', 0):,.2f}")
    print(f"Tax Payable: RM {record.get('tax_payable', 0):,.2f}")


# calculate tax with reliefs and save to CSV
def calculate_and_save_tax(user_id, ic_number, password, is_new_user=True):
    print("\n" + "==================================================")
    print("--- TAX CALCULATION ---")
    
    if is_new_user:
        print("Please enter your tax information.")
    else:
        print("Update your tax calculation with new information.")
    
    # get annual income
    while True:
        try:
            income_str = input("\nEnter your annual income (RM): ").strip()
            income = float(income_str)
            if income < 0:
                print("Income cannot be negative!")
                continue
            break
        except ValueError:
            print("Please enter a valid number!")
    
    # get detailed tax relief information from def tax_relief from functions2
    reliefs = tax_relief()
    
    # calculate tax from def calculate_tax from functions2
    tax_payable = calculate_tax(income, reliefs['total_relief'])
    chargeable = max(0, income - reliefs['total_relief'])

    # display tax relief info
    print("\n" + "============================================================")
    print("TAX RELIEF INFO")
    print(f"\nIndividual: RM {reliefs.get('individual_relief', 0):,.2f}")
    print(f"Spouse: RM {reliefs.get('spouse_relief', 0):,.2f}")
    print(f"Child: RM {reliefs.get('child_relief', 0):,.2f} ({reliefs.get('num_children', 0)} children)")
    print(f"Medical: RM {reliefs.get('medical_relief', 0):,.2f}")
    print(f"Lifestyle: RM {reliefs.get('lifestyle_relief', 0):,.2f}")
    print(f"Education: RM {reliefs.get('education_relief', 0):,.2f}")
    print(f"Parental Care: RM {reliefs.get('parental_relief', 0):,.2f}")
    print("------------------------------------------------------------")
    print(f"TOTAL TAX RELIEF: RM {reliefs['total_relief']:,.2f}")
    
    # display calculation results
    print("\n" + "============================================================")
    print("TAX CALCULATION RESULTS")
    print(f"\nUser ID: {user_id}")
    print(f"IC Number: {ic_number}")
    print(f"Annual Income: RM {income:,.2f}")
    print(f"Total Tax Relief: RM {reliefs['total_relief']:,.2f}")
    print(f"Chargeable Income: RM {chargeable:,.2f}")
    print(f"Tax Payable: RM {tax_payable:,.2f}")
    print("============================================================")
    
    # list all data to save it in CSV file
    data = {
        'id': user_id,
        'ic_number': ic_number,
        'password': password,
        'income': income,
        'individual_relief': reliefs.get('individual_relief', 0),
        'spouse_relief': reliefs.get('spouse_relief', 0),
        'child_relief': reliefs.get('child_relief', 0),
        'num_children': reliefs.get('num_children', 0),
        'medical_relief': reliefs.get('medical_relief', 0),
        'lifestyle_relief': reliefs.get('lifestyle_relief', 0),
        'education_relief': reliefs.get('education_relief', 0),
        'parental_relief': reliefs.get('parental_relief', 0),
        'total_relief': reliefs['total_relief'],
        'chargeable_income': chargeable,
        'tax_payable': tax_payable}
    
    # save to CSV
    if save_to_csv(data, update_existing=not is_new_user):
        print("\nTax record saved successfully!")
    else:
        print("\nError saving tax record!")
    
    return True


# display all tax records from CSV file 
def view_tax_records():
    print("\n" + "==================================================")
    print("--- TAX RECORDS ---")
    
    df = read_from_csv()
    if df is None or df.empty:
        print("No tax records found. Please calculate tax first.")
        return
    print(f"\nTotal Records: {len(df)}")
    print("\n" + "=======================================================================================")
    
    # Display records in a formatted way
    for index, row in df.iterrows():
        print(f"\nRecord #{index + 1}")
        print(f"  User ID: {row['id']}")
        print(f"  IC Number: {row['ic_number']}")
        print(f"  Income: RM {row['income']:,.2f}")
        print(f"\n  Tax Relief Breakdown:")
        print(f"    - Individual: RM {row.get('individual_relief', 0):,.2f}")
        print(f"    - Spouse: RM {row.get('spouse_relief', 0):,.2f}")
        print(f"    - Child ({int(row.get('num_children', 0))} kids): RM {row.get('child_relief', 0):,.2f}")
        print(f"    - Medical: RM {row.get('medical_relief', 0):,.2f}")
        print(f"    - Lifestyle: RM {row.get('lifestyle_relief', 0):,.2f}")
        print(f"    - Education: RM {row.get('education_relief', 0):,.2f}")
        print(f"    - Parental Care: RM {row.get('parental_relief', 0):,.2f}")
        print(f"  Total Relief: RM {row.get('total_relief', 0):,.2f}")
        print(f"  Chargeable: RM {row.get('chargeable_income', 0):,.2f}")
        print(f"  Tax Payable: RM {row['tax_payable']:,.2f}")

if __name__ == "__main__":
    main()