# ───────────────────────────────────────────────────────────── Dockerfile
FROM python:3.13-slim

# 1) basic housekeeping
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
WORKDIR /app

# 2) install deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 3) copy code and pre‑compute data
COPY . .
RUN python fetch_data.py && python analytics.py

# 4) expose port and start server
EXPOSE 8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
# ─────────────────────────────────────────────────────────────
