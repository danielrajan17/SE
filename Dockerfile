FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Pre-train model at build time
RUN python core/train.py

EXPOSE 8000
CMD ["python", "app/main.py"]
