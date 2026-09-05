import database
from user import User

class Customer(User):

    def menu(self):
        while True:
            print(f"""
===== Customer Menu ({self.name}) =====
1. Add a vehicle
2. View my vehicles
3. Update a vehicle
4. Delete a vehicle
5. Submit a service request
6. View my service requests
7. Update a service request
8. Cancel a service request
9. View my invoices
10. My profile
11. Update my profile
12. Logout
""")
            choice = input("Choice: ")
            if choice == '1':
                self.add_vehicle()
            elif choice == '2':
                self.view_my_vehicles()
            elif choice == '3':
                self.update_vehicle()
            elif choice == '4':
                self.delete_vehicle()
            elif choice == '5':
                self.submit_service_request()
            elif choice == '6':
                self.view_my_requests()
            elif choice == '7':
                self.update_service_request()
            elif choice == '8':
                self.cancel_service_request()
            elif choice == '9':
                self.view_my_invoices()
            elif choice == '10':
                self.view_profile()
            elif choice == '11':
                self.update_profile()
            elif choice == '12':
                print("Logged out")
                break
            else:
                print("Invalid choice")

    def add_vehicle(self):
        reg = input("Registration number: ")
        make = input("Make: ")
        model = input("Model: ")
        year = input("Year: ")
        fuel = input("Fuel type: ")
        try:
            database.c.execute("""
                INSERT INTO vehicles (owner_id, registration_number, make, model, year, fuel_type)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (self.user_id, reg, make, model, int(year) if year else None, fuel))
            database.conn.commit()
            print("Vehicle added successfully")
        except database.sqlite3.IntegrityError:
            print("A vehicle with that registration number already exists")
        except ValueError:
            print("Year must be a number")

    def view_my_vehicles(self):
        database.c.execute("SELECT * FROM vehicles WHERE owner_id = ?", (self.user_id,))
        rows = database.c.fetchall()
        if not rows:
            print("You have no registered vehicles")
        database.print_rows(rows)

    def _get_own_vehicle(self, vehicle_id):
        database.c.execute(
            "SELECT * FROM vehicles WHERE vehicle_id = ? AND owner_id = ?",
            (vehicle_id, self.user_id)
        )
        return database.c.fetchone()

    def update_vehicle(self):
        vid = input("Enter vehicle ID to update: ")
        row = self._get_own_vehicle(vid)
        if not row:
            print("Vehicle not found")
            return
        print("Leave a field blank to keep its current value.")
        make = input(f"Make [{row[3]}]: ") or row[3]
        model = input(f"Model [{row[4]}]: ") or row[4]
        year = input(f"Year [{row[5]}]: ") or row[5]
        fuel = input(f"Fuel type [{row[6]}]: ") or row[6]
        database.c.execute("""
            UPDATE vehicles SET make = ?, model = ?, year = ?, fuel_type = ? WHERE vehicle_id = ?
        """, (make, model, year, fuel, vid))
        database.conn.commit()
        print("Vehicle updated successfully")

    def delete_vehicle(self):
        vid = input("Enter vehicle ID to delete: ")
        if not self._get_own_vehicle(vid):
            print("Vehicle not found")
            return
        database.c.execute("DELETE FROM vehicles WHERE vehicle_id = ?", (vid,))
        database.conn.commit()
        print("Vehicle deleted successfully")

    def submit_service_request(self):
        self.view_my_vehicles()
        vid = input("Enter vehicle ID for this request: ")
        if not self._get_own_vehicle(vid):
            print("Vehicle not found")
            return
        issue = input("Describe the issue: ")
        database.c.execute("""
            INSERT INTO service_requests (vehicle_id, customer_id, issue_description)
            VALUES (?, ?, ?)
        """, (vid, self.user_id, issue))
        database.conn.commit()
        print("Service request submitted successfully")

    def view_my_requests(self):
        database.c.execute("SELECT * FROM service_requests WHERE customer_id = ?", (self.user_id,))
        rows = database.c.fetchall()
        if not rows:
            print("You have no service requests")
        database.print_rows(rows)

    def _get_own_request(self, request_id):
        database.c.execute(
            "SELECT * FROM service_requests WHERE request_id = ? AND customer_id = ?",
            (request_id, self.user_id)
        )
        return database.c.fetchone()

    def update_service_request(self):
        rid = input("Enter request ID to update: ")
        row = self._get_own_request(rid)
        if not row:
            print("Service request not found")
            return
        if row[5] != 'received':
            print("This request is already being processed and can no longer be edited")
            return
        issue = input(f"Issue description [{row[4]}]: ") or row[4]
        database.c.execute(
            "UPDATE service_requests SET issue_description = ? WHERE request_id = ?", (issue, rid)
        )
        database.conn.commit()
        print("Service request updated successfully")

    def cancel_service_request(self):
        rid = input("Enter request ID to cancel: ")
        row = self._get_own_request(rid)
        if not row:
            print("Service request not found")
            return
        if row[5] != 'received':
            print("This request is already being processed and can no longer be cancelled")
            return
        database.c.execute("DELETE FROM service_requests WHERE request_id = ?", (rid,))
        database.conn.commit()
        print("Service request cancelled")


    def view_my_invoices(self):
        database.c.execute("""
            SELECT i.* FROM invoices i
            JOIN service_requests r ON i.request_id = r.request_id
            WHERE r.customer_id = ?
        """, (self.user_id,))
        rows = database.c.fetchall()
        if not rows:
            print("You have no invoices")
        database.print_rows(rows)
