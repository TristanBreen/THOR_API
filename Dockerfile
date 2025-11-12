FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy dependency list and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire app
COPY . .

# Create data directory and initialize CSV files with headers
RUN mkdir -p /home/tristan/API/API_V2

# Initialize seizures.csv with headers if needed
RUN echo "Date,Time,Duration,Period,Eaten,FoodEaten" > /home/tristan/API/API_Repoed/seizures.csv

# Initialize pain.csv with headers
RUN echo "Date,Time,Pain" > /home/tristan/API/API_Repoed/pain.csv

# Expose the Flask port
EXPOSE 5000

# Run the Flask app
CMD ["python", "main.py"]