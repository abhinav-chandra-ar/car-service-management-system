import database

VALID_ROLES = ("admin", "customer", "mechanic", "coordinator")

class User:

    def __init__(self, row):
        self.user_id = row[0]
        self.name = row[1]
        self.username = row[2]
        self.role = row[4]

    @staticmethod
    def register(role):
        role = role.strip().lower()
        if role not in VALID_ROLES:
            print("Invalid role")
            return

        name = input("Enter your name : ")
        username = input("Enter your username : ")
        password = input("Enter your password : ")
        phone = input("Enter your phone number : ")
        email = input("Enter your email address : ")
        address = input("Enter your current address : ")

        try:
            database.c.execute("""
                INSERT INTO users (name, username, password, role, phone, email, address)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (name, username, password, role, phone, email, address))
            database.conn.commit()
            print("User created successfully")
        except database.sqlite3.IntegrityError:
            print("That username is already taken")

    @staticmethod
    def login():
        uname = input("Enter your username : ")
        pwd = input("Enter your password : ")
        database.c.execute("""
            SELECT * FROM users WHERE username = ? AND password = ?
        """, (uname, pwd))
        return database.c.fetchone()

    def view_profile(self):
        database.c.execute("SELECT * FROM users WHERE user_id = ?", (self.user_id,))
        row = database.c.fetchone()
        if not row:
            print("Profile not found")
            return
        print(f"""
ID       : {row[0]}
Name     : {row[1]}
Username : {row[2]}
Role     : {row[4]}
Phone    : {row[5]}
Email    : {row[6]}
Address  : {row[7]}
""")

    def update_profile(self):
        database.c.execute("SELECT * FROM users WHERE user_id = ?", (self.user_id,))
        row = database.c.fetchone()
        print("Leave a field blank to keep its current value.")
        name = input(f"Name [{row[1]}]: ") or row[1]
        phone = input(f"Phone [{row[5]}]: ") or row[5]
        email = input(f"Email [{row[6]}]: ") or row[6]
        address = input(f"Address [{row[7]}]: ") or row[7]
        database.c.execute("""
            UPDATE users SET name = ?, phone = ?, email = ?, address = ? WHERE user_id = ?
        """, (name, phone, email, address, self.user_id))
        database.conn.commit()
        self.name = name
        print("Profile updated successfully")

    def delete_account(self):
        confirm = input("Are you sure you want to delete your account? (yes/no): ")
        if confirm.lower() == 'yes':
            database.c.execute("DELETE FROM users WHERE user_id = ?", (self.user_id,))
            database.conn.commit()
            print("Account deleted")
            return True
        return False
