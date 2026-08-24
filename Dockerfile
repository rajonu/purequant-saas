FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY subscription_bot.py .
COPY data/ ./data/

CMD ["python3", "subscription_bot.py"]
