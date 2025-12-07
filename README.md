# FreeBites – Phase 3 

A complete **Flask + SQLite** implementation of the FreeBites food-distribution system for **CS2300 – Database Systems (Phase III)**.

This project includes:
- Full relational schema + automated database initialization  
- CRUD operations for events, food items, and student claims  
- Multi-table join queries and aggregation functions  
- Organizer & Student GUI dashboards  
- Completed final report (final_report.pdf)

---

## 🚀 Quick Start (Run the Project)

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

