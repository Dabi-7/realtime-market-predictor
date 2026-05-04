FROM python:3.10-slim

WORKDIR /app

run useradd -m con2

COPY requirements.txt

run pip install --no-cache-dir -r requirements.txt

COPY api/ /app/api

COPY final_weights/ app/models

RUN chown -R con2:con2 /app

USER con2

EXPOSE 8000

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000" ]
