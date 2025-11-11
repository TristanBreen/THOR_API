FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy dependency list and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire app
COPY . .

# Make sure the seizure log file exists (optional safeguard)
RUN mkdir -p /app/data && touch /app/data/seizures.csv

# Expose the Flask port
EXPOSE 5000

# Run the Flask app
CMD ["python", "main.py"]
