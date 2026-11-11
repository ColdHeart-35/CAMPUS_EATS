# README.md

## CampusEats – Canteen Pre‑Ordering and Inventory Management System

A lightweight full‑stack project for a college DBMS mini‑project. It showcases **PostgreSQL** relational concepts while providing a simple web interface for students, staff, and admins.

### Features
- Role‑based authentication (Student, Staff, Admin)
- Browse menu, manage cart, place orders (cash or demo payment)
- Staff order handling, inventory management, low‑stock alerts
- Admin dashboard with user and sales reports
- Comprehensive SQL scripts demonstrating the DBMS syllabus (DDL, DML, joins, subqueries, aggregates, CTEs, window functions, views, functions, procedures, triggers, indexes, transactions, etc.)

### Technology Stack
- **Frontend:** HTML, CSS, JavaScript (no frameworks)
- **Backend:** FastAPI (Python 3.11)
- **Database:** PostgreSQL (psycopg‑binary v3)
- **Auth:** JWT + password hashing (passlib, python‑jose)

### Project Structure
```
CampusEats/
├─ backend/
│  ├─ app/
│  │  ├─ main.py
│  │  ├─ database.py
│  │  ├─ auth/
│  │  │  ├─ __init__.py
│  │  │  ├─ security.py
│  │  │  └─ schemas.py
│  │  ├─ routes/
│  │  │  ├─ __init__.py
│  │  │  ├─ auth.py
│  │  │  ├─ student.py
│  │  │  ├─ staff.py
│  │  │  └─ admin.py
│  │  ├─ services/
│  │  │  ├─ __init__.py
│  │  │  ├─ user.py
│  │  │  ├─ food.py
│  │  │  ├─ order.py
│  │  │  └─ inventory.py
│  │  └─ utils/
│  │     ├─ __init__.py
│  │     └─ logger.py
│  └─ requirements.txt
├─ frontend/
│  ├─ index.html
│  ├─ css/
│  │  └─ styles.css
│  ├─ js/
│  │  └─ app.js
│  ├─ student/
│  │   └─ (student pages)
│  ├─ staff/
│  │   └─ (staff pages)
│  └─ admin/
│      └─ (admin pages)
├─ database/
│  ├─ 01_schema.sql
│  ├─ 02_constraints.sql
│  ├─ 03_seed_data.sql
│  ├─ 04_views.sql
│  ├─ 05_functions_procedures.sql
│  ├─ 06_triggers.sql
│  ├─ 07_indexes.sql
│  ├─ 08_queries.sql
│  ├─ 09_transactions.sql
│  └─ syllabus_demos/
│       ├─ demo_01_ddl_dml.sql
│       ├─ demo_02_joins.sql
│       └─ … (other demos)
├─ docs/
│  ├─ project_report.md
│  ├─ database_design.md
│  ├─ er_diagram.md
│  ├─ normalization.md
│  ├─ relational_algebra.md
│  ├─ api_documentation.md
│  ├─ setup_guide_fedora.md
│  ├─ testing_guide.md
│  └─ viva_questions.md
├─ .env.example
├─ .gitignore
└─ README.md
```

### Setup Guide (Fedora)
See `docs/setup_guide_fedora.md` for the exact commands.

---
*All code is static; you must run the commands manually on your Fedora system.*
