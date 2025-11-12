FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# REMOVE THESE LINES:
# RUN echo "Date,Time,Duration,Period,Eaten,FoodEaten" > seizures.csv
# RUN echo "Date,Time,Pain" > pain.csv

EXPOSE 5000
CMD ["python", "main.py"]