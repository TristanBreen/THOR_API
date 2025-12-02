# Seizure Prediction System

Machine learning system for predicting seizures and analyzing potential triggers.

## 📋 Overview

This system uses machine learning to:
1. **Predict when the next seizure will occur** (6-hour forecast window)
2. **Identify potential seizure triggers** from physiological, temporal, and lifestyle data

## 🗂️ Files

```
Prediction/
├── data_preprocessing.py    # Data loading and cleaning
├── feature_engineering.py   # Feature creation
├── train_model.py          # Model training
├── predict.py              # Real-time predictions
├── analyze_triggers.py     # Trigger analysis
├── requirements.txt        # Python dependencies
└── models/                 # Saved models (created after training)
```

## 🚀 Installation

1. Install dependencies:
```bash
cd Prediction
pip install -r requirements.txt
```

## 📊 Data Requirements

The system expects three CSV files in the `../Data/` folder:

1. **seizures.csv**: Seizure events with date, time, duration
2. **appleWatchData.csv**: Hourly health metrics (heart rate, sleep, activity)
3. **pain.csv**: Pain level recordings

## 🎯 Usage

### First Time Setup - Train Models

```bash
python train_model.py
```

This will:
- Load and process all data
- Create 100+ features
- Train classification and regression models
- Save trained models to `models/` folder
- Display performance metrics and top important features

**Expected Output:**
```
Training samples: ~2500
Seizure prediction ROC-AUC: 0.75-0.85
Time prediction MAE: 2-4 hours
```

### Analyze Seizure Triggers

```bash
python analyze_triggers.py
```

This provides comprehensive analysis of:
- **Temporal patterns**: Most common hours/days for seizures
- **Physiological patterns**: Heart rate differences before seizures
- **Sleep patterns**: Sleep quality correlation
- **Pain patterns**: Pain level associations
- **Activity patterns**: Physical activity correlations
- **Food patterns**: Dietary factors
- **Inter-seizure intervals**: Time between seizures

### Get Real-Time Predictions

```bash
python predict.py
```

This shows:
- Current seizure risk probability
- Predicted hours until next seizure
- Risk level (Low, Moderate, Elevated, High, Very High)
- 24-hour forecast with high-risk periods
- Recent seizure history

## 🧠 How It Works

### 1. Feature Engineering

The system creates 100+ features including:

**Temporal Features:**
- Hour of day, day of week, weekend indicator
- Cyclical encodings (sine/cosine) for time patterns

**Seizure History Features:**
- Hours since last seizure
- Number of seizures in past 24h, 48h, 72h, 1 week
- Average time between seizures

**Physiological Features:**
- Heart rate min/max/average
- Rolling statistics (6h, 12h, 24h windows)
- Heart rate variability proxy

**Sleep Features:**
- Total sleep, deep sleep, REM sleep
- Sleep quality ratios
- Recent sleep patterns (forward-filled up to 24h)

**Pain Features:**
- Current pain level
- Rolling averages and maximums
- Pain change rate

**Activity Features:**
- Walking/running distance
- Activity rolling sums and averages
- Activity change patterns

### 2. Machine Learning Models

**Classification Model** (Seizure in next 6 hours?):
- Random Forest or Gradient Boosting
- Predicts probability (0-100%)
- Class balanced for imbalanced data

**Regression Model** (Hours until next seizure):
- Random Forest Regressor
- Predicts continuous time value
- Useful for detailed planning

### 3. Model Performance

Typical performance metrics:
- **ROC-AUC**: 0.75-0.85 (good discrimination)
- **Precision/Recall**: Balanced to minimize false alarms while catching true positives
- **MAE**: 2-4 hours (time prediction accuracy)

## 📈 Most Important Features

Based on typical training, key predictive features include:

1. **Hours since last seizure** - Strong cyclical pattern
2. **Time of day** - Certain hours show higher risk
3. **Heart rate patterns** - Changes in HR 6-12h before
4. **Sleep quality** - Poor sleep increases risk
5. **Recent seizure frequency** - Clustering effects
6. **Pain levels** - Elevated pain correlates with risk

## 🔄 Retraining the Model

As new data accumulates, retrain the model:

```bash
python train_model.py
```

**When to retrain:**
- Every 1-2 weeks as new data arrives
- After significant pattern changes
- When prediction accuracy decreases

The system automatically:
- Loads latest CSV data from `../Data/`
- Creates new features
- Retrains models
- Saves new models with timestamp
- Updates `models/..._latest.pkl` files

## 🎨 Customization

### Adjust Prediction Window

In `train_model.py`, change:
```python
predictor = SeizurePredictor(prediction_horizon=6)  # Default: 6 hours
```

Options: 3, 6, 12, 24 hours

### Risk Thresholds

In `predict.py`, modify `_get_risk_level()`:
```python
def _get_risk_level(self, probability):
    if probability < 0.2:    # Adjust thresholds
        return 'Low'
    elif probability < 0.4:
        return 'Moderate'
    # ...
```

## 📱 Integration with Dashboard

To integrate with your dashboard (`webpage/app.py`):

```python
from Prediction.predict import SeizureForecaster

forecaster = SeizureForecaster()
summary = forecaster.get_summary()

# Use in your Flask app
@app.route('/api/seizure-prediction')
def get_prediction():
    return jsonify(summary)
```

## 🔍 Understanding Results

### Seizure Probability
- **0-20%**: Low risk, normal activities OK
- **20-40%**: Moderate risk, be aware
- **40-60%**: Elevated risk, take precautions
- **60-80%**: High risk, avoid triggers
- **80-100%**: Very high risk, seek support

### Predicted Hours
- Continuous estimate of time until next seizure
- Use with probability for comprehensive picture
- More reliable when probability is high

## 🐛 Troubleshooting

**"FileNotFoundError" for CSV files:**
- Ensure CSV files are in `../Data/` folder
- Check file names match exactly

**"Models not found" error:**
- Run `python train_model.py` first
- Check `models/` folder exists

**Poor prediction accuracy:**
- Ensure at least 2-3 months of data
- Check data quality (missing values)
- Retrain model with latest data

**Memory errors:**
- Reduce feature windows in `feature_engineering.py`
- Use smaller dataset for testing

## 📊 Example Output

```
==================================================================
SEIZURE PREDICTION SUMMARY
==================================================================

📊 CURRENT PREDICTION
----------------------------------------------------------------------
Timestamp: 2025-11-28 12:00:00
Seizure Probability: 23.4%
Predicted Time to Next Seizure: 18.3 hours
Risk Level: Moderate

📈 RECENT HISTORY
----------------------------------------------------------------------
Time Since Last Seizure: 72.5 hours (3.0 days)
Total Seizures Recorded: 21

🕐 LAST 5 SEIZURES
----------------------------------------------------------------------
1. 2025-11-28 15:29:14 - Duration: 82 seconds
2. 2025-11-20 15:48:21 - Duration: 55 seconds
3. 2025-11-14 13:29:01 - Duration: 100 seconds
4. 2025-11-05 09:03:02 - Duration: 59 seconds
5. 2025-11-04 13:16:33 - Duration: 120 seconds
```

## 🔬 Advanced Usage

### Export Predictions to CSV

```python
from predict import SeizureForecaster

forecaster = SeizureForecaster()
forecast = forecaster.get_forecast(hours_ahead=168)  # 1 week
forecast.to_csv('forecast_output.csv', index=False)
```

### Batch Analysis

```python
from analyze_triggers import TriggerAnalyzer
from data_preprocessing import DataLoader

loader = DataLoader()
df, seizures = loader.create_hourly_dataset()
analyzer = TriggerAnalyzer()
results = analyzer.analyze_all_triggers(df, seizures)

# Results saved to models/trigger_analysis.json
```

## 📝 Notes

- Model accuracy improves with more data (3+ months ideal)
- Regular retraining recommended as patterns may change
- Predictions are probabilistic, not deterministic
- Always consult healthcare providers for medical decisions
- Use as a supportive tool, not sole decision-maker

## 🤝 Support

For issues or questions, check:
1. Ensure all CSV files are up-to-date
2. Verify Python version (3.8+ required)
3. Check all dependencies installed
4. Review error messages carefully

---

**Last Updated:** 2025-11-28  
**Version:** 1.0.0