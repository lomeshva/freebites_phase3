# FreeBites – Phase 3 Demo (v2)

This folder is a self‑contained Flask + SQLite project.

## Quick start

```bash
cd freebites_final_project_v2

python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

pip install flask

python -c "from src.db import init_db; init_db(); print('DB ready')" 

export FLASK_APP=run.py
flask run
```

Login accounts:

* Organizer – `alice@campus.edu` / `1234`
* Student   – `bob@campus.edu`   / `5678`
