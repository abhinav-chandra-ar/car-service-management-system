from user import User
from admin import Admin
from customer import Customer
from mechanic import Mechanic
from coordinator import ServiceCoordinator

def crud_account(row):
    role = row[4]
    mapping = {
        "admin": Admin,
        "customer": Customer,
        "mechanic": Mechanic,
        "coordinator": ServiceCoordinator
        }

    if role in mapping :
        return mapping[role](row)
    else:
        return None

while True:
    print("===== 1. Register =====\n===== 2. Login =====\n===== 3. Exit =====")
    choice = input()
    if choice == '1':
        role = input("Register as (admin/customer/mechanic/coordinator): ")
        User.register(role)
    elif choice == '2':
        row = User.login()
        if row is None:
            print("Invalid credentials")
        else:
            account = crud_account(row)
            if account is None:
                print("Unknown role on this account")
            else:
                account.menu()
    elif choice == '3':
        break
    else:
        print("Invalid choice")