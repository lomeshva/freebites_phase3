# FreeBites – Phase 3 

A complete **Flask + SQLite** implementation of the FreeBites food-distribution system for **CS2300 – Database Systems (Phase III)**.

This project includes:
- Full relational schema + automated database initialization  
- CRUD operations for events, food items, and student claims  
- Multi-table join queries and aggregation functions  
- Organizer & Student GUI dashboards  
- Completed final report (final_report.pdf)

---

## Quick Start (Run the Project)

```bash
cd freebites_phase3

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate     # Windows: .venv\Scripts\activate

# Install dependencies
pip install flask

# Initialize database (tables + sample data)
python -c "from src.db import init_db; init_db(); print('DB ready')"

# Start application
export FLASK_APP=run.py
flask run
```
## Application URL
The app will run at:  
**http://127.0.0.1:5000**

---

## Login Accounts (for Testing)

### Organizer  
- **Email:** `alice@campus.edu`  
- **Password:** `1234`

### Student  
- **Email:** `bob@campus.edu`  
- **Password:** `5678`

---

## Project Structure

```
instance/            # auto-generated SQLite database
sql/                 # init_db.sql (schema + inserts)
src/
  app.py             # Flask routes + GUI logic
  db.py              # CRUD operations, joins, aggregation
static/css/
  style.css          # UI styling
templates/           # HTML pages (Organizer & Student)
run.py               # Application entry point
final_report.pdf     # Full Phase III documentation
README.md
```

