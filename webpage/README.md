# Seizure Monitoring Dashboard

A minimal, self-contained web application for visualizing seizure data from a CSV file.

## Features

- **Real-time Data Visualization**: Interactive charts showing seizure patterns and trends
- **Summary Statistics**: Total seizures, averages, and key metrics
- **Modern Design**: Clean, editorial-style interface with soft cream background and charcoal accents
- **Responsive Layout**: Works on desktop and mobile devices
- **Easy Deployment**: Simple Flask application with minimal dependencies

## Installation

1. Navigate to the webpage directory:
```bash
cd webpage
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Ensure the seizures.csv file exists in the parent directory (../seizures.csv)

## Running the Application

```bash
python3 app.py
```

The application will start on http://localhost:5000

## CSV File Format

The seizures.csv file should have the following columns:
- timestamp (datetime)
- seizure_type (text)
- duration_seconds (numeric)
- severity (text: High/Medium/Low)
- location (text)
- notes (text)

## Visualizations

1. **Daily Seizure Frequency**: Line chart showing daily trends
2. **Seizure Types Distribution**: Pie chart of seizure type frequencies
3. **Average Duration by Type**: Horizontal bar chart
4. **Weekly Trends**: Bar chart showing weekly patterns
5. **Seizure Timeline**: Scatter plot with seizure types and severity

## Technology Stack

- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3, JavaScript
- **Charts**: Plotly.js
- **Styling**: Custom CSS with editorial design principles

## Notes

- The application automatically filters out NULL values from the dataset
- Data is read from ../seizures.csv (parent directory)
- The server refreshes data on each page load
- Charts are fully interactive with hover effects and zoom capabilities