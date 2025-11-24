# 🏥 THOR API - Health Tracking & Monitoring System

**T**ristan's **H**ome **O**perational **R**epository

A comprehensive health monitoring system designed to track seizures and pain levels with automated logging, visualization, and notifications. Written by Sonnet 4.5.

### CHECK OUT THE RUNNING DASHBOARD: http://68.0.162.91:5001/

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [System Architecture](#system-architecture)
- [Installation](#installation)
- [API Documentation](#api-documentation)
- [Dashboard](#dashboard)
- [Deployment](#deployment)
- [Configuration](#configuration)
- [Data Storage](#data-storage)
- [Security Notes](#security-notes)
- [Contributing](#contributing)

---

## 🎯 Overview

THOR API is a Flask-based REST API and web dashboard system that provides:

- **Seizure tracking** with detailed metadata (duration, food intake, menstrual cycle correlation)
- **Pain level monitoring** on a 1-10 scale
- **Automated email notifications** when seizures are logged
- **Predictive analytics** for seizure patterns
- **Interactive dashboard** with comprehensive data visualization
- **Good morning messages** with weather and fun facts

---

## ✨ Features

### Core Functionality

- 📊 **Real-time Data Tracking**: Log seizures and pain levels via simple API calls
- 📧 **Email Notifications**: Automatic email alerts with attached data files
- 🌤️ **Weather Integration**: Fetches current weather from the National Weather Service API
- 🤖 **AI-Powered Fun Facts**: Daily interesting facts powered by Google Gemini API
- 📈 **Predictive Analysis**: Estimates next seizure occurrence based on historical patterns
- 🎨 **Beautiful Dashboard**: Modern, responsive web interface with interactive charts

### Dashboard Features

- **Summary Statistics**: Total seizures, averages, trends, and key metrics
- **Interactive Charts**:
  - Seizure risk heatmap (hour × day of week)
  - Monthly and daily frequency trends
  - Duration distribution analysis
  - Time between seizures
  - Food correlation analysis
  - Pain tracking with seizure event markers
- **Smart Filtering**: Filter by date range, period, and food intake
- **Data Export**: Download complete dataset as CSV
- **Real-time Updates**: Auto-refresh every 30 seconds

---

## 🏗️ System Architecture

```
THOR_API/
├── main.py                 # Main Flask API application
├── config.py               # Configuration (API keys, credentials)
├── emailSeizureLogs.py     # Email notification module
├── requirements.txt        # Python dependencies
├── pain.csv               # Pain tracking data
├── seizures.csv           # Seizure tracking data
├── .github/
│   └── workflows/
│       └── deploy.yml     # CI/CD deployment workflow
└── webpage/
    ├── app.py             # Dashboard Flask application
    ├── requirements.txt   # Dashboard dependencies
    ├── templates/
    │   └── dashboard.html # Dashboard interface
    └── README.md          # Dashboard documentation
```

---

## 🚀 Installation

### Prerequisites

- Python 3.8+
- pip package manager
- Git

### Setup Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd THOR_API
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**
   
   Create a `config.py` file with your credentials:
   ```python
   GEMINI_API_KEY = "your_gemini_api_key"
   GMAIL_PASSCODE_FOR_AUTOMATION = "your_gmail_app_password"
   ```

4. **Run the API**
   ```bash
   python main.py
   ```
   
   The API will be available at `http://localhost:5000`

5. **Run the Dashboard** (optional)
   ```bash
   cd webpage
   pip install -r requirements.txt
   python app.py
   ```
   
   Dashboard will be available at `http://localhost:5000`

---

## 📡 API Documentation

### Base URL
```
http://localhost:5000
```

### Endpoints

#### 🌅 Good Morning Message
Get a personalized morning greeting with weather and fun fact.

```http
GET /goodmorning?lat={latitude}&lon={longitude}
```

**Parameters:**
- `lat` (float, required): Latitude coordinate
- `lon` (float, required): Longitude coordinate

**Response:**
```json
{
  "message": "Good morning! Rise and shine! Currently it is 72 degrees with a high of 85 degrees. Did you know that..."
}
```

---

#### 🔴 Log Seizure
Record a seizure event with detailed metadata.

```http
GET /seizure?duration={seconds}&period={yes/no}&eaten={yes/no}&foodEaten={description}
```

**Parameters:**
- `duration` (int, required): Seizure duration in seconds
- `period` (string, required): "Yes" or "No" - menstrual cycle status
- `eaten` (string, required): "Yes" or "No" - whether food was consumed
- `foodEaten` (string, optional): Description of food eaten (if `eaten=Yes`)

**Response:**
```json
{
  "message": "Seizure for 120 seconds has been logged"
}
```

**Side Effects:**
- Logs entry to `seizures.csv`
- Sends email notification with attached CSV file

---

#### 💊 Log Pain Level
Record current pain level on a scale of 1-10 (attempting to use entire scale consistently).

```http
GET /pain?pain={level}
```

**Parameters:**
- `pain` (int, required): Pain level from 1-10

**Response:**
```json
{
  "message": "Pain has been logged"
}
```

---

#### 📅 Next Seizure Prediction
Get an estimate of when the next seizure may occur based on historical patterns.

```http
GET /nextseizure
```

**Response:**
```json
{
  "message": "Next seizure should be in 5 days."
}
```

**Note:** Calculation assumes a 14-day cycle based on historical data.

---

## 📊 Dashboard

The web dashboard provides comprehensive visualization and analysis of health data.

### Accessing the Dashboard

```bash
cd webpage
python app.py
```

Visit `http://localhost:5000` in your browser.

### Dashboard Sections

1. **Statistics Overview**
   - Total seizures tracked
   - Recent activity (last 7 days)
   - Average duration and frequency
   - Food and period correlations

2. **Key Insights**
   - Peak time patterns
   - Weekly patterns
   - Food correlation analysis
   - Period tracking summary

3. **Visualizations**
   - Seizure risk heatmap
   - Hour of day analysis
   - Duration distribution
   - Monthly trends
   - Time between seizures
   - Pain tracking timeline

4. **Data Table**
   - Filterable record list
   - Sort by date, period, food intake
   - Export to CSV

### Dashboard Features

- 🎨 **Modern Design**: Clean, editorial-style interface with nature-inspired color scheme
- 📱 **Responsive**: Works on desktop, tablet, and mobile devices
- 🔄 **Auto-Refresh**: Updates every 30 seconds
- 📥 **Data Export**: Download complete dataset as CSV
- 🔍 **Smart Filtering**: Filter records by multiple criteria

---

## 🚢 Deployment

The repository includes automated deployment via GitHub Actions.

### Deployment Workflow

The `.github/workflows/deploy.yml` file handles:

1. **Automated backups** of CSV data files
2. **Git management** (stashing local changes, pulling latest)
3. **Docker rebuild** for API and webpage services
4. **Graceful stash reapplication**

### Deployment Trigger

Deployment runs automatically on push to `main` branch:

```yaml
on:
  push:
    branches: ["main"]
```

### Manual Deployment

```bash
# Restart Flask service
sudo systemctl restart flask.service

# Or rebuild Docker containers
cd /path/to/Docker
docker compose up -d --build thor-api thor-webpage
```

---

## ⚙️ Configuration

### Required API Keys

1. **Google Gemini API Key**
   - Used for generating fun facts
   - Get it from: https://makersuite.google.com/app/apikey

2. **Gmail App Password**
   - Used for email notifications
   - Create at: https://myaccount.google.com/apppasswords

### Email Configuration

Edit `emailSeizureLogs.py` to customize:

```python
USERNAME = "your-email@gmail.com"
TO = "recipient@gmail.com"
```

### Weather Location

Default location is set to Tempe, Arizona. Modify coordinates in API calls:

```python
# Example: Phoenix, AZ
lat = 33.4484
lon = -112.0740
```

---

## 💾 Data Storage

### Seizures CSV Format

```csv
Date,Time,Duration,Period,Eaten,FoodEaten
2025-11-14,13:29:01,100,False,False,
2025-11-05,09:03:02,59,False,False,
```

**Columns:**
- `Date`: YYYY-MM-DD format
- `Time`: HH:MM:SS format
- `Duration`: Seconds (integer)
- `Period`: Boolean (True/False)
- `Eaten`: Boolean (True/False)
- `FoodEaten`: Text description (optional)

### Pain CSV Format

```csv
Date,Time,Pain
2025-11-14,13:29:26,8
2025-11-14,10:14:59,6
```

**Columns:**
- `Date`: YYYY-MM-DD format
- `Time`: HH:MM:SS format
- `Pain`: Integer (1-10 scale)

### Data Backup

Automated backups are created during deployment:

```
deploy_backups/
├── pain_20251115120000.csv
├── seizures_20251115120000.csv
└── ...
```

---

## 🔒 Security Notes

### ⚠️ IMPORTANT: Protect Sensitive Data

1. **Never commit `config.py`** to version control
   ```bash
   echo "config.py" >> .gitignore
   ```

2. **Use environment variables** for production:
   ```python
   import os
   GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
   GMAIL_PASSCODE = os.getenv('GMAIL_PASSCODE')
   ```

3. **Rotate credentials** regularly

4. **Limit API access** with firewall rules or authentication middleware

### Current Security Concerns

⚠️ **Action Required**: Your `config.py` contains plaintext credentials that should be removed from the repository immediately.

---

## 🛠️ Dependencies

### Main API
```
flask
requests
google-generativeai
```

### Dashboard
```
Flask==2.3.3
pandas==2.0.3
gunicorn==21.2.0
```

---

## 📝 Contributing

### Development Workflow

1. Create a feature branch
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes

3. Test locally
   ```bash
   python main.py
   cd webpage && python app.py
   ```

4. Commit and push
   ```bash
   git add .
   git commit -m "Description of changes"
   git push origin feature/your-feature-name
   ```

5. Create a pull request to `main`

---

## 📄 License

This project is private and intended for personal use.

---

## 🙏 Acknowledgments

- **Weather Data**: National Weather Service API
- **AI Fun Facts**: Google Gemini API
- **Charts**: Chart.js
- **Design Inspiration**: Editorial and nature-inspired design principles

---

## 📞 Support

For issues or questions, please open an issue in the repository.

---

**Built with ❤️ for health monitoring and peace of mind**
