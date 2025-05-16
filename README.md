# eCFR Analyzer — Demo

> **⚠️ Evaluation‑Only:** This project is a time‑boxed technical assignment.  It is **not** licensed for production or internal use unless I am hired or a formal contract is executed.

## Quick Start (local)
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python fetch_data.py
python analytics.py
uvicorn app:app --reload  # API at http://localhost:8000/metrics