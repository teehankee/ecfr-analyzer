FROM python:3.12-slim
WORKDIR /app
COPY . .

RUN pip install -r requirements.txt

# --- NEW: pull eCFR + build metrics right in the image -------------
RUN python fetch_data.py && python analytics.py

EXPOSE 8000
CMD [".venv/bin/uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
