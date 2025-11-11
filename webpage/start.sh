#!/bin/bash
# Start the Seizure Monitoring Dashboard

echo "Starting Seizure Monitoring Dashboard..."
echo "Make sure seizures.csv exists in the parent directory"
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "Starting Flask application..."
echo "Dashboard will be available at: http://localhost:5000"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python3 app.py