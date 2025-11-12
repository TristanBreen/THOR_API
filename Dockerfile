FROM python:3.11-slim

# Set timezone to Arizona
ENV TZ=America/Phoenix
RUN apt-get update && apt-get install -y tzdata && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000
CMD ["python", "main.py"]