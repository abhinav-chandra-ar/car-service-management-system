import database
from user import User, VALID_ROLES

class Admin(User):

    def menu(self):
        while True:
            print(f"""
===== Admin Menu ({self.name}) =====
1. View all users
2. View a user
3. Update a user
4. Delete a user
5. View all vehicles
6. View all service requests
7. My profile
8. Update my profile
9. Logout
""")
            choice = input("Choice: ")
            if choice == '1':
                self.view_all_users()
            elif choice == '2':
                self.view_user()
            elif choice == '3':
                self.update_user()
            elif choice == '4':
                self.delete_user()
            elif choice == '5':
                self.view_all_vehicles()
            elif choice == '6':
                self.view_all_requests()
            elif choice == '7':
                self.view_profile()
            elif choice == '8':
                self.update_profile()
            elif choice == '9':
                print("Logged out")
                break
            else:
                print("Invalid choice")

    def view_all_users(self):
        database.c.execute("SELECT user_id, name, username, role, phone, email FROM users")
        rows = database.c.fetchall()
        if not rows:
            print("No users found")
        database.print_rows(rows)

    def view_user(self):
        uid = input("Enter user ID: ")
        database.c.execute("SELECT * FROM users WHERE user_id = ?", (uid,))
        row = database.c.fetchone()
        if row:
            database.print_row(row)
        else:
            print("User not found")

    def update_user(self):
        uid = input("Enter user ID to update: ")
        database.c.execute("SELECT * FROM users WHERE user_id = ?", (uid,))
        row = database.c.fetchone()
        if not row:
            print("User not found")
            return
        print("Leave a field blank to keep its current value.")
        name = input(f"Name [{row[1]}]: ") or row[1]
        role = input(f"Role [{row[4]}]: ") or row[4]
        if role not in VALID_ROLES:
            print("Invalid role")
            return
        phone = input(f"Phone [{row[5]}]: ") or row[5]
        email = input(f"Email [{row[6]}]: ") or row[6]
        address = input(f"Address [{row[7]}]: ") or row[7]
        database.c.execute("""
            UPDATE users SET name = ?, role = ?, phone = ?, email = ?, address = ?
            WHERE user_id = ?
        """, (name, role, phone, email, address, uid))
        database.conn.commit()
        print("User updated successfully")

    def delete_user(self):
        uid = input("Enter user ID to delete: ")
        confirm = input("Are you sure? (yes/no): ")
        if confirm.lower() != 'yes':
            return
        database.c.execute("DELETE FROM users WHERE user_id = ?", (uid,))
        database.conn.commit()
        print("User deleted" if database.c.rowcount else "User not found")

    def view_all_vehicles(self):
        database.c.execute("""
            SELECT v.vehicle_id, v.registration_number, v.make, v.model, v.year, u.name AS owner
            FROM vehicles v JOIN users u ON v.owner_id = u.user_id
        """)
        rows = database.c.fetchall()
        if not rows:
            print("No vehicles found")
        database.print_rows(rows)

    def view_all_requests(self):
        database.c.execute("SELECT * FROM service_requests")
        rows = database.c.fetchall()
        if not rows:
            print("No service requests found")
        database.print_rows(rows)
