# PNES (Psychogenic Non-Epileptic Seizures) Detection System

## Overview

The THOR_API dashboard now includes an advanced PNES (Psychogenic Non-Epileptic Seizures) detection system that analyzes seizure patterns to help differentiate between psychological and neurological seizure disorders.

## What is PNES?

PNES are seizure-like episodes that originate from psychological factors rather than neurological dysfunction. While the symptoms appear similar to epileptic seizures, they are driven by psychological processes such as:

- Stress and anxiety
- Trauma
- Emotional distress
- Environmental triggers
- Subconscious psychological conflicts

PNES affects approximately 15-25% of patients diagnosed with "refractory epilepsy" who don't respond to anti-seizure medications.

## How PNES Detection Works

The system analyzes **5 key indicators** to generate a PNES likelihood score (0-100):

### 1. **Pain/Anxiety Correlation** (Weight: 20 points)
- **What it measures**: Correlation between pain records and seizure occurrence
- **PNES indicator**: PNES seizures are often triggered by stress, anxiety, and emotional pain
- **High PNES risk**: >50% of seizure days have associated pain records
- **Example**: If a patient has 20 seizure days and pain documented on 11+ of those days, this suggests psychological triggers

### 2. **Daytime Predominance** (Weight: 15 points)
- **What it measures**: Percentage of seizures occurring during waking hours (7 AM - 11 PM)
- **PNES indicator**: PNES typically occur when the patient is conscious and aware
- **High PNES risk**: >70% of seizures occur during daytime
- **Example**: Epileptic seizures often occur during sleep; PNES rarely do
- **Clinical significance**: Nocturnal seizures strongly suggest epilepsy

### 3. **Duration Variability** (Weight: 12 points)
- **What it measures**: Coefficient of Variation (CV) in seizure duration
- **PNES indicator**: PNES have highly inconsistent durations; epileptic seizures are more consistent
- **High PNES risk**: CV > 50% (high variability)
- **Calculation**: CV = (Standard Deviation / Mean Duration) × 100
- **Example**: If durations range from 30 seconds to 5 minutes, this suggests PNES

### 4. **Environmental/Food Triggers** (Weight: 10 points)
- **What it measures**: Correlation between food intake and seizure occurrence
- **PNES indicator**: Seizures triggered by specific environments or emotional contexts
- **High PNES risk**: Food-related seizures deviate significantly from 50% (either >60% or <40%)
- **Example**: If seizures occur almost exclusively when NOT eating, this suggests psychological triggers

### 5. **Hormonal Correlation** (Weight: 8 points)
- **What it measures**: Percentage of seizures related to menstrual cycle
- **Epilepsy indicator**: Catamenial (menstrual-related) epilepsy is well-documented
- **Low PNES risk**: <20% period-related seizures suggests psychological rather than hormonal origin
- **Example**: Reflex seizures with low hormonal correlation suggest PNES

## PNES Risk Classification

The system assigns one of four classifications based on the total score:

| Classification | Score Range | Clinical Meaning | Recommendation |
|---|---|---|---|
| **HIGH** | 50-100 | Strong psychological indicators | Neuropsychiatric evaluation recommended |
| **MODERATE** | 30-49 | Mixed psychological/neurological | Psychological screening recommended |
| **LOW** | 15-29 | Primarily neurological indicators | Continue standard epilepsy management |
| **MINIMAL** | 0-14 | Strong neurological indicators | Standard epilepsy protocols |

## Risk Factors Display

The dashboard displays identified risk factors with:

- **Indicator name**: The specific pattern identified
- **Score**: Percentage or numeric value of the indicator
- **Description**: Clinical explanation of what was detected
- **PNES Relevance**: How this indicator relates to PNES diagnosis

## Clinical Recommendations

Based on the classification level, the system provides tailored recommendations:

### HIGH PNES Risk Recommendations:
1. Consider psychological evaluation by neuropsychiatrist
2. EEG monitoring recommended to rule out subclinical seizures
3. Stress/anxiety assessment and management program suggested
4. Keep detailed trigger logs (emotional events, stressors)

### MODERATE PNES Risk Recommendations:
1. Psychological screening recommended
2. Continue seizure tracking with emotional/stress context
3. Consider video-EEG monitoring if diagnosis uncertain

### LOW/MINIMAL PNES Risk Recommendations:
1. Continue standard epilepsy management
2. Monitor for changes in seizure pattern
3. Maintain detailed seizure logs

## Data Requirements

For accurate PNES analysis, the system needs:

1. **Seizure records** with:
   - Date and time of seizure
   - Duration (in seconds)
   - Associated food intake (yes/no)
   - Menstrual period status (yes/no)

2. **Pain/stress records** with:
   - Date of pain event
   - Severity or presence indicator

3. **Health data** (optional):
   - Heart rate trends
   - Sleep patterns
   - Activity levels

## Integration Points

### React Frontend Component: `PNESAnalysis.tsx`
Located in `/components/PNESAnalysis.tsx`

- Displays PNES likelihood score with visual progress bar
- Shows classification badge with color coding
- Lists all detected risk factors with detailed explanations
- Provides clinical recommendations
- Includes medical disclaimer

### Next.js API Route: `pages/api/data.ts`
Function: `analyzePNESIndicators()`

- Analyzes seizure patterns in real-time
- Calculates all 5 PNES indicators
- Returns structured PNES analysis data
- Integrated into main `/api/data` response

### Flask Backend: `app.py` (Optional)
- Imports `pnes_analyzer` module for Python-based analysis
- Adds PNES results to `/api/data` endpoint
- Can be used for enhanced statistical analysis

## Medical Disclaimer

⚠️ **Important**: This analysis is based on seizure patterns, triggers, and clinical indicators. A definitive PNES diagnosis requires:

1. **Comprehensive medical evaluation** by a qualified neurologist
2. **Video-EEG monitoring** to rule out epileptic activity
3. **Psychiatric assessment** by a trained mental health professional
4. Clinical correlation with patient history

The PNES detection system is a **screening tool only** and should not replace professional medical diagnosis.

## Usage Examples

### Example 1: Clear PNES Pattern
- 28 seizures, 25 with associated pain (89% correlation)
- 26 seizures during daytime (93% daytime)
- Duration CV: 62% (highly variable)
- 18 seizures with food intake (64% food-related)
- 2 seizures during period (7% hormonal)
- **Result**: PNES Likelihood = 65 (HIGH RISK) ⚠️

### Example 2: Clear Epilepsy Pattern
- 30 seizures, 8 with associated pain (27% correlation)
- 8 seizures during daytime (27% daytime, 73% at night)
- Duration CV: 18% (consistent)
- 15 seizures with food, 15 without (50% food-related)
- 12 seizures during period (40% hormonal)
- **Result**: PNES Likelihood = 8 (MINIMAL RISK) ✓

### Example 3: Uncertain Pattern
- 20 seizures, 10 with associated pain (50% correlation)
- 14 seizures during daytime (70% daytime)
- Duration CV: 35% (moderate variability)
- 7 seizures with food (35% food-related)
- 6 seizures during period (30% hormonal)
- **Result**: PNES Likelihood = 27 (LOW RISK) - Requires further evaluation

## Future Enhancements

Potential improvements to the PNES detection system:

1. **Machine Learning Integration**: Train models on known PNES vs. epilepsy cases
2. **EEG Integration**: Incorporate actual EEG findings
3. **Behavioral Tracking**: Add emotional state, stress levels, life events
4. **Video Analysis**: Automated video-EEG classification
5. **Predictive Alerts**: Predict high-risk periods for PNES events
6. **Longitudinal Tracking**: Monitor changes in PNES indicators over time
7. **Medication Correlation**: Track anti-seizure medication effectiveness

## References

- American Epilepsy Society. (2020). Non-epileptic seizures: Update on recognition and management.
- Kanemoto, K., et al. (2020). Prevalence and outcome of psychogenic non-epileptic seizures in Japan. Epilepsia.
- LaFrance, W. C., et al. (2020). Psychogenic non-epileptic seizures: A practical update. CNS Spectrums.

## API Response Structure

The PNES analysis is included in the `/api/data` response:

```json
{
  "pnes_analysis": {
    "pnes_likelihood_score": 35,
    "classification": "MODERATE",
    "risk_factors": [
      {
        "indicator": "High Anxiety/Pain Correlation",
        "score": "65.0",
        "description": "65.0% of seizure days have associated pain records",
        "pnes_relevance": "HIGH - PNES often triggered by psychological stress"
      }
    ],
    "recommendations": [
      "Psychological screening recommended",
      "Continue seizure tracking with emotional/stress context",
      "Consider video-EEG monitoring if diagnosis uncertain"
    ]
  }
}
```

## Contact & Support

For questions about the PNES detection system, please contact the THOR_API development team or your healthcare provider.
