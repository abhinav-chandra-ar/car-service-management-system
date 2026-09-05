import database
from user import User

class Mechanic(User):

    def menu(self):
        while True:
            print(f"""
===== Mechanic Menu ({self.name}) =====
1. View my assigned jobs
2. Update job status
3. Add part used on a job
4. View parts used on a job
5. Update part usage
6. Remove part usage
7. My profile
8. Update my profile
9. Logout
""")
            choice = input("Choice: ")
            if choice == '1':
                self.view_assigned_jobs()
            elif choice == '2':
                self.update_job_status()
            elif choice == '3':
                self.add_part_used()
            elif choice == '4':
                self.view_parts_used()
            elif choice == '5':
                self.update_part_used()
            elif choice == '6':
                self.remove_part_used()
            elif choice == '7':
                self.view_profile()
            elif choice == '8':
                self.update_profile()
            elif choice == '9':
                print("Logged out")
                break
            else:
                print("Invalid choice")

    def _get_assigned_job(self, request_id):
        database.c.execute(
            "SELECT * FROM service_requests WHERE request_id = ? AND mechanic_id = ?",
            (request_id, self.user_id)
        )
        return database.c.fetchone()

    def view_assigned_jobs(self):
        database.c.execute("SELECT * FROM service_requests WHERE mechanic_id = ?", (self.user_id,))
        rows = database.c.fetchall()
        if not rows:
            print("No jobs assigned to you")
        database.print_rows(rows)

    def update_job_status(self):
        rid = input("Enter request ID: ")
        if not self._get_assigned_job(rid):
            print("Job not found or not assigned to you")
            return
        print("Valid statuses: in_progress, completed")
        status = input("New status: ").strip().lower()
        if status not in ('in_progress', 'completed'):
            print("Invalid status")
            return
        if status == 'completed':
            database.c.execute("""
                UPDATE service_requests SET status = ?, date_completed = CURRENT_TIMESTAMP
                WHERE request_id = ?
            """, (status, rid))
        else:
            database.c.execute(
                "UPDATE service_requests SET status = ? WHERE request_id = ?", (status, rid)
            )
        database.conn.commit()
        print("Job status updated")

    def add_part_used(self):
        rid = input("Enter request ID: ")
        if not self._get_assigned_job(rid):
            print("Job not found or not assigned to you")
            return
        database.c.execute("SELECT * FROM inventory_parts")
        parts = database.c.fetchall()
        if not parts:
            print("No parts available in inventory")
            return
        database.print_rows(parts)
        pid = input("Enter part ID to use: ")
        database.c.execute("SELECT * FROM inventory_parts WHERE part_id = ?", (pid,))
        part = database.c.fetchone()
        if not part:
            print("Part not found")
            return
        try:
            qty = int(input("Quantity used: "))
        except ValueError:
            print("Invalid quantity")
            return
        if qty <= 0 or qty > part[3]:
            print("Invalid quantity or insufficient stock")
            return
        database.c.execute("""
            INSERT INTO service_parts_used (request_id, part_id, quantity_used, price_at_time)
            VALUES (?, ?, ?, ?)
        """, (rid, pid, qty, part[2]))
        database.c.execute(
            "UPDATE inventory_parts SET stock_quantity = stock_quantity - ? WHERE part_id = ?",
            (qty, pid)
        )
        database.conn.commit()
        print("Part usage recorded")

    def view_parts_used(self):
        rid = input("Enter request ID: ")
        database.c.execute("""
            SELECT spu.usage_id, ip.part_name, spu.quantity_used, spu.price_at_time
            FROM service_parts_used spu JOIN inventory_parts ip ON spu.part_id = ip.part_id
            WHERE spu.request_id = ?
        """, (rid,))
        rows = database.c.fetchall()
        if not rows:
            print("No parts recorded for this request")
        database.print_rows(rows)

    def update_part_used(self):
        uid = input("Enter usage ID to update: ")
        database.c.execute("SELECT * FROM service_parts_used WHERE usage_id = ?", (uid,))
        row = database.c.fetchone()
        if not row:
            print("Usage record not found")
            return
        database.c.execute("SELECT stock_quantity FROM inventory_parts WHERE part_id = ?", (row[2],))
        stock = database.c.fetchone()[0]
        try:
            new_qty = int(input(f"New quantity [{row[3]}]: ") or row[3])
        except ValueError:
            print("Invalid quantity")
            return
        diff = new_qty - row[3]
        if diff > stock:
            print("Insufficient stock for this change")
            return
        database.c.execute(
            "UPDATE service_parts_used SET quantity_used = ? WHERE usage_id = ?", (new_qty, uid)
        )
        database.c.execute(
            "UPDATE inventory_parts SET stock_quantity = stock_quantity - ? WHERE part_id = ?",
            (diff, row[2])
        )
        database.conn.commit()
        print("Part usage updated")

    def remove_part_used(self):
        uid = input("Enter usage ID to remove: ")
        database.c.execute("SELECT * FROM service_parts_used WHERE usage_id = ?", (uid,))
        row = database.c.fetchone()
        if not row:
            print("Usage record not found")
            return
        database.c.execute("DELETE FROM service_parts_used WHERE usage_id = ?", (uid,))
        database.c.execute(
            "UPDATE inventory_parts SET stock_quantity = stock_quantity + ? WHERE part_id = ?",
            (row[3], row[2])
        )
        database.conn.commit()
        print("Part usage removed and stock restored")
