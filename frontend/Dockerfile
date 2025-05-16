# Dockerfile  (repo root)

FROM python:3.12-slim

# 0️⃣ create non‑root user so fly’s auto‑stop works happily
RUN adduser --disabled-password --gecos '' appuser
WORKDIR /app
USER appuser

# 1️⃣ copy deps & install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 2️⃣ copy source
COPY . .

# 3️⃣ bake eCFR data into the image (one‑time fetch)
RUN python fetch_data.py && python analytics.py

EXPOSE 8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
