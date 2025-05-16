FROM python:3.12-slim

WORKDIR /app
COPY . .

# Install everything (make sure uvicorn is in requirements.txt)
RUN pip install --no-cache-dir -r requirements.txt

# Pre‑compute your data (optional – comment out if you’ll load on start‑up)
RUN python fetch_data.py && python analytics.py

# 🔑 Tell Fly how to start your API  — no .venv path needed
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
