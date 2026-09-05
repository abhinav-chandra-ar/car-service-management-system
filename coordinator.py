import database
from user import User

class ServiceCoordinator(User):

    def menu(self):
        while True:
            print(f"""
===== Coordinator Menu ({self.name}) =====
1. View all service requests
2. Assign a mechanic to a request
3. Add inventory part
4. View inventory parts
5. Update inventory part
6. Delete inventory part
7. Generate invoice
8. View invoices
9. Update invoice
10. Delete invoice
11. My profile
12. Update my profile
13. Logout
""")
            choice = input("Choice: ")
            if choice == '1':
                self.view_all_requests()
            elif choice == '2':
                self.assign_mechanic()
            elif choice == '3':
                self.add_part()
            elif choice == '4':
                self.view_parts()
            elif choice == '5':
                self.update_part()
            elif choice == '6':
                self.delete_part()
            elif choice == '7':
                self.generate_invoice()
            elif choice == '8':
                self.view_invoices()
            elif choice == '9':
                self.update_invoice()
            elif choice == '10':
                self.delete_invoice()
            elif choice == '11':
                self.view_profile()
            elif choice == '12':
                self.update_profile()
            elif choice == '13':
                print("Logged out")
                break
            else:
                print("Invalid choice")

    def view_all_requests(self):
        database.c.execute("SELECT * FROM service_requests")
        rows = database.c.fetchall()
        if not rows:
            print("No service requests found")
        database.print_rows(rows)

    def assign_mechanic(self):
        rid = input("Enter request ID: ")
        database.c.execute("SELECT * FROM service_requests WHERE request_id = ?", (rid,))
        if not database.c.fetchone():
            print("Service request not found")
            return
        database.c.execute("SELECT user_id, name FROM users WHERE role = 'mechanic'")
        mechanics = database.c.fetchall()
        if not mechanics:
            print("No mechanics available")
            return
        database.print_rows(mechanics)
        mid = input("Enter mechanic ID to assign: ")
        database.c.execute(
            "UPDATE service_requests SET mechanic_id = ?, status = 'assigned' WHERE request_id = ?",
            (mid, rid)
        )
        database.conn.commit()
        print("Mechanic assigned successfully")

    def add_part(self):
        name = input("Part name: ")
        try:
            price = float(input("Unit price: "))
            qty = int(input("Stock quantity: "))
        except ValueError:
            print("Invalid price or quantity")
            return
        database.c.execute(
            "INSERT INTO inventory_parts (part_name, unit_price, stock_quantity) VALUES (?, ?, ?)",
            (name, price, qty)
        )
        database.conn.commit()
        print("Part added successfully")

    def view_parts(self):
        database.c.execute("SELECT * FROM inventory_parts")
        rows = database.c.fetchall()
        if not rows:
            print("No parts in inventory")
        database.print_rows(rows)

    def update_part(self):
        pid = input("Enter part ID to update: ")
        database.c.execute("SELECT * FROM inventory_parts WHERE part_id = ?", (pid,))
        row = database.c.fetchone()
        if not row:
            print("Part not found")
            return
        name = input(f"Part name [{row[1]}]: ") or row[1]
        try:
            price = float(input(f"Unit price [{row[2]}]: ") or row[2])
            qty = int(input(f"Stock quantity [{row[3]}]: ") or row[3])
        except ValueError:
            print("Invalid price or quantity")
            return
        database.c.execute("""
            UPDATE inventory_parts SET part_name = ?, unit_price = ?, stock_quantity = ?
            WHERE part_id = ?
        """, (name, price, qty, pid))
        database.conn.commit()
        print("Part updated successfully")

    def delete_part(self):
        pid = input("Enter part ID to delete: ")
        database.c.execute("DELETE FROM inventory_parts WHERE part_id = ?", (pid,))
        database.conn.commit()
        print("Part deleted" if database.c.rowcount else "Part not found")

    def generate_invoice(self):
        rid = input("Enter request ID to invoice: ")
        database.c.execute("SELECT * FROM service_requests WHERE request_id = ?", (rid,))
        if not database.c.fetchone():
            print("Service request not found")
            return
        database.c.execute("SELECT invoice_id FROM invoices WHERE request_id = ?", (rid,))
        if database.c.fetchone():
            print("An invoice already exists for this request")
            return
        database.c.execute(
            "SELECT COALESCE(SUM(quantity_used * price_at_time), 0) FROM service_parts_used WHERE request_id = ?",
            (rid,)
        )
        parts_cost = database.c.fetchone()[0]
        try:
            labor = float(input("Labor cost: "))
        except ValueError:
            print("Invalid labor cost")
            return
        total = labor + parts_cost
        database.c.execute("""
            INSERT INTO invoices (request_id, coordinator_id, labor_cost, parts_cost, total_cost)
            VALUES (?, ?, ?, ?, ?)
        """, (rid, self.user_id, labor, parts_cost, total))
        database.conn.commit()
        print(f"Invoice generated. Parts cost: {parts_cost}, Labor cost: {labor}, Total: {total}")

    def view_invoices(self):
        database.c.execute("SELECT * FROM invoices")
        rows = database.c.fetchall()
        if not rows:
            print("No invoices found")
        database.print_rows(rows)

    def update_invoice(self):
        iid = input("Enter invoice ID to update: ")
        database.c.execute("SELECT * FROM invoices WHERE invoice_id = ?", (iid,))
        row = database.c.fetchone()
        if not row:
            print("Invoice not found")
            return
        try:
            labor = float(input(f"Labor cost [{row[3]}]: ") or row[3])
        except ValueError:
            print("Invalid labor cost")
            return
        print("Payment status: unpaid / paid")
        payment_status = input(f"Payment status [{row[7]}]: ") or row[7]
        total = labor + row[4]
        database.c.execute("""
            UPDATE invoices SET labor_cost = ?, total_cost = ?, payment_status = ?
            WHERE invoice_id = ?
        """, (labor, total, payment_status, iid))
        database.conn.commit()
        print("Invoice updated successfully")

    def delete_invoice(self):
        iid = input("Enter invoice ID to delete: ")
        database.c.execute("DELETE FROM invoices WHERE invoice_id = ?", (iid,))
        database.conn.commit()
        print("Invoice deleted" if database.c.rowcount else "Invoice not found")
