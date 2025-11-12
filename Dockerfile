FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy dependency list and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire app
COPY . .

# Initialize CSV files with headers in the working directory
RUN echo "Date,Time,Duration,Period,Eaten,FoodEaten" > seizures.csv
RUN echo "Date,Time,Pain" > pain.csv

# Expose the Flask port
EXPOSE 5000

# Run the Flask app
CMD ["python", "main.py"]