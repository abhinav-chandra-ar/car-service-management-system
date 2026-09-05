import sqlite3

conn = sqlite3.connect('car_service_system.db')
c = conn.cursor()

c.execute("PRAGMA foreign_keys = ON")

c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        role TEXT NOT NULL,
        phone TEXT NOT NULL,
        email TEXT,
        address TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
""")

c.execute("""
    CREATE TABLE IF NOT EXISTS vehicles (
        vehicle_id INTEGER PRIMARY KEY AUTOINCREMENT,
        owner_id INTEGER NOT NULL,
        registration_number TEXT NOT NULL UNIQUE,
        make TEXT NOT NULL,
        model TEXT NOT NULL,
        year INTEGER,
        fuel_type TEXT,
        FOREIGN KEY (owner_id) REFERENCES users(user_id) ON DELETE CASCADE
    )
""")

c.execute("""
    CREATE TABLE IF NOT EXISTS service_requests (
        request_id INTEGER PRIMARY KEY AUTOINCREMENT,
        vehicle_id INTEGER NOT NULL,
        customer_id INTEGER NOT NULL,
        date_submitted TEXT DEFAULT CURRENT_TIMESTAMP,
        issue_description TEXT,
        status TEXT NOT NULL DEFAULT 'received',
        mechanic_id INTEGER,
        date_completed TEXT,
        FOREIGN KEY (vehicle_id) REFERENCES vehicles(vehicle_id) ON DELETE CASCADE,
        FOREIGN KEY (customer_id) REFERENCES users(user_id) ON DELETE CASCADE,
        FOREIGN KEY (mechanic_id) REFERENCES users(user_id)
    )
""")

c.execute("""
    CREATE TABLE IF NOT EXISTS inventory_parts (
        part_id INTEGER PRIMARY KEY AUTOINCREMENT,
        part_name TEXT NOT NULL,
        unit_price REAL NOT NULL,
        stock_quantity INTEGER NOT NULL DEFAULT 0
    )
""")

c.execute("""
    CREATE TABLE IF NOT EXISTS service_parts_used (
        usage_id INTEGER PRIMARY KEY AUTOINCREMENT,
        request_id INTEGER NOT NULL,
        part_id INTEGER NOT NULL,
        quantity_used INTEGER NOT NULL,
        price_at_time REAL NOT NULL,
        FOREIGN KEY (request_id) REFERENCES service_requests(request_id) ON DELETE CASCADE,
        FOREIGN KEY (part_id) REFERENCES inventory_parts(part_id)
    )
""")

c.execute("""
    CREATE TABLE IF NOT EXISTS invoices (
        invoice_id INTEGER PRIMARY KEY AUTOINCREMENT,
        request_id INTEGER NOT NULL UNIQUE,
        coordinator_id INTEGER NOT NULL,
        labor_cost REAL NOT NULL,
        parts_cost REAL NOT NULL,
        total_cost REAL NOT NULL,
        date_issued TEXT DEFAULT CURRENT_TIMESTAMP,
        payment_status TEXT DEFAULT 'unpaid',
        FOREIGN KEY (request_id) REFERENCES service_requests(request_id) ON DELETE CASCADE,
        FOREIGN KEY (coordinator_id) REFERENCES users(user_id)
    )
""")

conn.commit()


def print_row(row):
    """Print a single fetched row as 'column: value' pairs, using the
    column names of the query that produced it."""
    if row is None:
        print("Not found")
        return
    columns = [d[0] for d in c.description]
    print(" | ".join(f"{col}: {value}" for col, value in zip(columns, row)))


def print_rows(rows):
    """Print each row from a fetchall() result as 'column: value' pairs."""
    for row in rows:
        print_row(row)