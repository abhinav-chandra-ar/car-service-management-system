# Car Service Management System

A console-based (terminal) Car Service Management System built in Python with an SQLite database. It supports four user roles — **Admin**, **Customer**, **Mechanic**, and **Coordinator** — each with their own menu and permissions, covering the full flow of a vehicle service center: registering vehicles, submitting service requests, assigning mechanics, tracking parts inventory, and generating invoices.

## Features by Role

**Admin**
- View all users / view a single user
- Update or delete a user
- View all vehicles
- View all service requests
- View and update own profile

**Customer**
- Add / view / update / delete their own vehicles
- Submit a service request for a vehicle
- View their service requests
- Update or cancel a request (only while its status is still `received`)
- View their invoices
- View and update own profile

**Mechanic**
- View jobs assigned to them
- Update a job's status (`in_progress` / `completed`)
- Record parts used on a job (auto-deducts from inventory stock)
- View, update, or remove a part-usage record (stock is adjusted accordingly)
- View and update own profile

**Coordinator**
- View all service requests
- Assign a mechanic to a request
- Add / view / update / delete inventory parts
- Generate an invoice for a request (labor cost + parts cost used on that job)
- View, update, or delete invoices (including marking payment status as paid/unpaid)
- View and update own profile

All roles share: **Register** (choose a role and create an account) and **Login** (username + password).

## Requirements

- Python 3.10 or newer (standard install includes the `sqlite3` module — no extra packages needed)
- No third-party libraries required (see `requirements.txt`)
- Works on Windows, macOS, or Linux

## Project Structure

```
Car_Service_System/
├── main.py              # Entry point — Register/Login loop, routes to each role's menu
├── user.py               # Base User class — register, login, view/update profile (shared by all roles)
├── admin.py               # Admin role menu and actions
├── customer.py            # Customer role menu and actions
├── mechanic.py            # Mechanic role menu and actions
├── coordinator.py         # Coordinator role menu and actions
├── database.py            # SQLite connection + table creation + shared print helpers
├── schema.sql             # Standalone copy of the database schema (for documentation/reference)
├── car_service_system.db  # SQLite database file (created automatically on first run)
├── requirements.txt       # Dependency notes (none required — stdlib only)
└── screenshots/           # Screenshots of the running application
```

## How It Works (Architecture)

- `main.py` is the entry point. It shows a Register/Login/Exit menu in a loop.
- `user.py` defines the base `User` class with the logic shared by every role: registering an account, logging in, viewing/updating a profile.
- Each role (`Admin`, `Customer`, `Mechanic`, `ServiceCoordinator`) is a subclass of `User` defined in its own file, adding a `menu()` method and the actions specific to that role.
- After a successful login, `main.py` looks at the `role` column on the account and instantiates the matching subclass, then calls its `menu()`.
- `database.py` opens the single SQLite connection (`car_service_system.db`) shared by the whole program, creates all tables if they don't already exist, and provides two small helpers (`print_row` / `print_rows`) used everywhere to print query results in a readable `column: value` format.

## Usage Guide

When you run `python main.py` you'll see:
```
===== 1. Register =====
===== 2. Login =====
===== 3. Exit =====
```

**First time using it:** choose `1` to register. You'll be asked to pick a role (`admin`, `customer`, `mechanic`, or `coordinator`) and enter your name, username, password, phone, email, and address.

**After that:** choose `2` to log in with your username and password. You'll land on the menu for your role (see "Features by Role" above) — enter the number next to an option to use it, and follow the prompts.

A typical end-to-end flow, using four accounts (one per role):

1. **Customer** registers, logs in, adds a vehicle, and submits a service request describing the issue.
2. **Coordinator** logs in, views all service requests, and assigns a mechanic to the new request.
3. **Mechanic** logs in, sees the job under "assigned jobs", updates its status to `in_progress`, records any parts used (this deducts stock automatically), then marks it `completed`.
4. **Coordinator** logs in again and generates an invoice for that request — labor cost is entered manually, parts cost is calculated automatically from the parts recorded by the mechanic.
5. **Customer** logs in and views their invoice under "View my invoices".
6. **Admin** can log in at any point to view/manage all users, vehicles, and requests.

## Database Schema

SQLite database `car_service_system.db`, 6 tables.

| Table | Purpose | Key columns |
|---|---|---|
| `users` | One row per registered account of any role | `user_id` (PK), `username` (unique), `password`, `role` |
| `vehicles` | Vehicles registered by a customer | `vehicle_id` (PK), `owner_id` → `users.user_id`, `registration_number` (unique) |
| `service_requests` | A customer's request to service a vehicle | `request_id` (PK), `vehicle_id` → `vehicles`, `customer_id` → `users`, `mechanic_id` → `users`, `status` |
| `inventory_parts` | Spare parts stock | `part_id` (PK), `unit_price`, `stock_quantity` |
| `service_parts_used` | Parts consumed on a specific job | `usage_id` (PK), `request_id` → `service_requests`, `part_id` → `inventory_parts`, `quantity_used`, `price_at_time` |
| `invoices` | Final bill for a completed request | `invoice_id` (PK), `request_id` → `service_requests` (unique, one invoice per request), `labor_cost`, `parts_cost`, `total_cost`, `payment_status` |

**Relationships**
- One user (customer) → many vehicles.
- One vehicle → many service requests.
- One service request → optionally one mechanic (assigned by a coordinator), many parts-used rows, and at most one invoice.
- `service_requests.status` moves through: `received` → `assigned` → `in_progress` → `completed`.
- Deleting a user/vehicle/request cascades to delete its dependent vehicles/requests/parts-used/invoice rows (`ON DELETE CASCADE`), so no orphaned data is left behind.


## Known Limitations

- Passwords are stored as plain text in the database (fine for an academic project, not for production use).
- The application is single-user/single-terminal — there's no concurrent multi-user server component.
- No automated tests are included yet.

## Author

Abhinav — MCA student, Amrita Vishwa Vidyapeetham, Kochi.
