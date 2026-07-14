FROM python:3.10
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod -R 777 /app
ENV TRANSFORMERS_CACHE=/app/.cache
ENV HF_HOME=/app/.cache

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]