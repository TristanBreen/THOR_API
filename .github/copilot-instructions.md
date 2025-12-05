# THOR API - Copilot Instructions

## 🎯 Project Overview

**THOR API** is a personal health monitoring system for tracking seizures and pain levels with ML-powered predictive analytics, automated email notifications, and an interactive dashboard. It consists of three interconnected Flask applications:

1. **Main API** (`main.py`) - REST endpoint for logging seizures/pain, weather integration, fun facts
2. **Prediction System** (`Prediction/`) - ML pipeline for seizure forecasting
3. **Dashboard** (`webpage/app.py`) - Data visualization and interactive charts

## 📁 Architecture & Data Flow

### Directory Structure
```
THOR_API/
├── main.py                          # Flask REST API (port 5000)
├── config.py                        # API keys (Gemini, Gmail)
├── emailSeizureLogs.py              # Email notification module
├── Prediction/
│   ├── train_model.py               # SeizurePredictor class - trains classification/regression models
│   ├── data_preprocessing.py        # DataLoader - loads/cleans CSVs
│   ├── feature_engineering.py       # FeatureEngineer - creates 100+ features
│   ├── predict.py                   # SeizureForecaster - real-time predictions
│   ├── analyze_triggers.py          # Trigger analysis (temporal, physiological patterns)
│   ├── prediction_feedback.py       # Feedback mechanisms for model refinement
│   └── models/                      # Serialized models (feature_importance.json, trigger_analysis.json)
├── webpage/
│   ├── app.py                       # Dashboard Flask app (port 5001)
│   ├── templates/dashboard.html     # Frontend - interactive charts, filtering
│   └── static/                      # CSS/JS assets
└── Data/
    ├── seizures.csv                 # Event log: Date, Time, Duration, Period, Eaten, Food Eaten
    ├── appleWatchData.csv           # Hourly metrics: Heart Rate, Sleep, Activity, Distance
    ├── pain.csv                     # Pain tracking: Date, Time, Pain (1-10 scale)
    ├── prediction.txt               # Current predictions (updated by predict.py)
    └── longTermPredictions.json     # Historical predictions with timestamps
```

### Critical Data Flow
1. **CSV Input** → `DataLoader.create_hourly_dataset()` merges hourly Apple Watch data with seizure/pain events
2. **Feature Engineering** → `FeatureEngineer.create_features()` generates temporal, physiological, and historical features
3. **Model Training** → `SeizurePredictor.train()` fits classification (seizure probability) + regression (hours until seizure) models
4. **Predictions** → `SeizureForecaster.get_forecast()` generates rolling 24/48/72-hour forecasts
5. **Dashboard** → Reads CSVs directly, caches data for 60 seconds, displays interactive charts

### Path Resolution Pattern
All modules handle cross-platform deployment by checking paths in priority order:
```python
SERVER_BASE_PATH = "/home/tristan/API/API_Repoed/THOR_API"  # Production server path
if os.path.exists(os.path.join(SERVER_BASE_PATH, "Data")):
    BASE_DATA_DIR = SERVER_BASE_PATH
elif os.path.exists('/data/Data'):  # Docker mount
    BASE_DATA_DIR = '/data/Data'
else:  # Local development
    BASE_DATA_DIR = os.path.join(parent_dir, "Data")
```
**When modifying file I/O**: Always use this pattern; never hardcode absolute paths.

## 🤖 Key Machine Learning Concepts

### Models Architecture (Prediction/train_model.py)
- **Classification Model**: RandomForest/GradientBoosting predicts binary seizure occurrence within horizon (default 6h)
- **Regression Model**: RandomForest predicts hours until next seizure
- **Sample Weights**: Leverages `prediction_feedback.py` to weight recent/accurate predictions higher

### Feature Engineering (100+ Features)
```python
# Temporal: hour, day_of_week, month, hour_sin/cos, dow_sin/cos (cyclical encoding)
# Physiological: avg/min/max heart rate, heart_rate_variability, resting_heart_rate
# Sleep: total_sleep, deep_sleep, rem_sleep, sleep_quality_score
# Activity: walking_distance, activity_minutes
# Seizure History: days_since_last_seizure, seizures_in_last_7d/14d/30d, avg_duration
# Pain: pain_level, pain_frequency_7d
# Food: eaten_in_last_24h (boolean), time_since_eating
# Feedback Features: recent_accuracy_score, adjustment_factor (added via prediction_feedback.py)
```

### Data Preprocessing Edge Cases
- **Missing Values**: First fill with column means, then fill remaining NaNs with 0
- **Duration Cleaning**: `pd.to_numeric(..., errors='coerce')` converts malformed duration values to NaN
- **Boolean Parsing**: Maps 'True'/'False'/'NULL' strings to Python booleans/None
- **Hourly Alignment**: `create_hourly_dataset()` creates a complete hourly grid and forward-fills missing physiological data

## 🔄 Common Development Workflows

### Running Predictions Locally
```bash
cd Prediction
python predict.py  # Generates 24/48/72-hour forecasts, updates prediction.txt and longTermPredictions.json
```

### Training Models (After Data Updates)
```bash
cd Prediction
python train_model.py  # Trains both classification/regression models, saves to models/
                       # Expected output: ROC-AUC 0.75-0.85, MAE 2-4 hours
```

### Analyzing Trigger Patterns
```bash
python analyze_triggers.py  # Identifies temporal, physiological, sleep, pain, activity, food patterns
                            # Saves feature importance to models/feature_importance.json
                            # Saves trigger analysis to models/trigger_analysis.json
```

### Dashboard Testing
```bash
cd webpage
python app.py  # Starts on http://localhost:5001
               # Auto-refreshes data every 30 seconds; cache invalidates on seizure/pain logging
```

### Docker Deployment
```bash
docker-compose up -d  # Starts thor-api (5000), thor-webpage (5001), jellyfin (8096), pinchflat
                       # Data directory mounted as /data in containers
```

## 🚀 Deployment & Integration

### Automatic Deployment
- **CI/CD**: GitHub Actions workflow (`.github/workflows/deploy.yml`) handles pushes to `main` branch
- **Server**: Deployed to `68.0.162.91` on home server

### Critical Integration Points
1. **Email Notifications**: `emailSeizureLogs.py` sends CSV snapshots when seizure logged (requires Gmail app password in `config.py`)
2. **Gemini API**: `main.py` fetches daily fun facts and uses in good morning message
3. **National Weather Service**: Fetches current weather for good morning message
4. **Data Consistency**: Dashboard and prediction system both read same CSV files; cache invalidation on updates ensures sync

## 📊 API Endpoints (main.py)

- `GET /` - Good morning message with weather and fun facts
- `GET /api/summary` - Comprehensive summary (predictions, recent seizures, data stats)
- `POST /api/seizure` - Log seizure event (triggers email notification)
- `POST /api/pain` - Log pain level
- `GET /api/seizures` - Retrieve seizure history (JSON)
- `GET /api/pain` - Retrieve pain history (JSON)

## 🎨 Dashboard Implementation (webpage/)

### Key Design Patterns
- **CachedDataStore**: Thread-safe LRU cache (60-second TTL) prevents redundant CSV reads
- **Interactive Charts**: Built with Chart.js or similar; fetch JSON endpoints from `/api/` routes
- **Real-time Filtering**: Frontend filters by date range, period status, food intake without backend calls
- **Data Export**: Downloads raw CSV for external analysis

### Common Dashboard Queries
- **Seizure Risk Heatmap**: Hour × day_of_week grid showing avg seizure probability
- **Monthly Trends**: Aggregates seizures per day; shows frequency distribution
- **Time Between Seizures**: Calculates inter-seizure intervals; plots histogram
- **Food Correlation**: Compares seizure count when eaten vs. fasted
- **Pain vs. Seizures**: Overlay of pain levels and seizure events on timeline

## 🛠️ Common Coding Patterns & Conventions

### Model Saving/Loading
```python
# Save: models stored in Prediction/models/ using joblib
joblib.dump(model, os.path.join(MODEL_DIR, 'classification_model.joblib'))

# Load: SeizurePredictor.load_model() reads from models/
predictor.load_model('models')
```

### Configuration Management
- `config.py` holds API keys (Gemini, Gmail)
- Never commit sensitive data; use environment variables for CI/CD
- Optional import pattern for graceful degradation: `try/except ImportError`

### Error Handling in CSV Operations
- Always use `.fillna()` and `.copy()` to avoid SettingWithCopyWarning
- Use `safe_float()` helper in dashboard for handling NaN/null values
- Validate CSV structure before model training; log warnings for missing columns

### Path Independence
- Every module resolves paths independently—don't assume relative imports from parent modules
- Use `os.path.dirname(os.path.abspath(__file__))` for script location, then navigate from there
- Test changes both locally (relative paths) and in Docker (mounted `/data`)

## ⚠️ Critical Gotchas

1. **Datetime Alignment**: Seizure events are point-in-time; Apple Watch data is hourly. `create_hourly_dataset()` creates complete hourly grid and aligns events. Any datetime manipulation must preserve this alignment.

2. **Prediction Horizon**: Default is 6 hours. Changing this requires retraining models and updating `SeizurePredictor.__init__()` instantiation everywhere.

3. **CSV Write Conflicts**: Use atomic writes (`tempfile + os.replace()`) in `predict.py` to avoid partial writes during concurrent dashboard reads.

4. **Cache Invalidation**: Dashboard cache must be explicitly invalidated after seizure/pain logging (see `cache_store.invalidate()`).

5. **Model Versioning**: Models are not versioned; training on new data overwrites old models. Keep timestamped backups if A/B testing is needed.

## 📚 Key Files to Reference

| File | Purpose | Critical Functions |
|------|---------|-------------------|
| `Prediction/data_preprocessing.py` | Data loading | `DataLoader.create_hourly_dataset()` |
| `Prediction/feature_engineering.py` | Feature creation | `FeatureEngineer.create_features()` |
| `Prediction/train_model.py` | Model training | `SeizurePredictor.train()`, `.predict()` |
| `Prediction/predict.py` | Real-time forecasting | `SeizureForecaster.get_forecast()` |
| `webpage/app.py` | Dashboard backend | `load_seizure_data()`, `/api/` routes |
| `main.py` | REST API | Seizure/pain logging endpoints |

---

**Before making changes:**
1. Understand data flow from CSV → features → predictions → dashboard
2. Check if changes affect model retraining (may break forecasts until retrained)
3. Test file I/O on both local paths and Docker mounts
4. Verify all `create_hourly_dataset()` calls use consistent parameters
