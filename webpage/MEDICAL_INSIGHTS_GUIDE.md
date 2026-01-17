# Advanced Medical Insights Documentation

## Overview

The THOR_API dashboard now includes **Advanced Medical Insights** - a comprehensive clinical analysis section designed specifically for healthcare providers and medical researchers to identify patterns and correlations in seizure data.

## Key Medical Insights

### 1. 🍽️ Food Impact Analysis

**What It Measures:**
- Compares average seizure duration when food was eaten vs. when fasting
- Calculates the difference and identifies the direction of impact
- Tracks total number of food-related vs. non-food-related seizures

**Clinical Significance:**
- **Longer seizures with food**: May indicate food sensitivities or triggers that exacerbate seizure severity
- **Shorter seizures with food**: May suggest certain foods have protective or stabilizing effects
- **No difference**: Suggests food is not a significant seizure trigger

**Example Data:**
```
With Food: 95 seconds (12 events)
Without Food: 78 seconds (8 events)
Difference: +17 seconds (Seizures 18% longer with food)
Implication: Patient may have food-triggered PNES or food-sensitive epilepsy
```

**Doctor Actions:**
- Recommend elimination diet to identify specific triggers
- Refer to nutritionist for dietary management
- Consider food as potential PNES trigger if other factors present

---

### 2. 🩸 Menstrual Cycle Analysis

**What It Measures:**
- Compares seizure duration during menstrual period vs. other times
- Calculates percentage of seizures related to menstrual cycle
- Identifies "catamenial" seizure patterns

**Clinical Significance:**
- **Catamenial Epilepsy**: Seizures that cluster around menstrual cycle (specifically ~3 days before, during, and after period)
- **Hormonal Influence**: Estrogen/progesterone fluctuations affect seizure threshold
- **Treatment Implications**: May warrant hormonally-based treatments (perimenstrual therapy)

**Categories:**
- **Perimenstrual**: 3 days before through 3 days after period (highest risk)
- **Catamenial**: >2x seizures during this window vs. other times
- **Nonmenstrual Pattern**: Seizures independent of cycle

**Example Data:**
```
During Period: 102 seconds (8 seizures)
Outside Period: 75 seconds (22 seizures)
Period Percentage: 26.7% of total seizures
Classification: Catamenial Pattern Likely
```

**Doctor Actions:**
- Refer to gynecologist for hormonal evaluation
- Consider perimenstrual therapy (additional medication during at-risk window)
- Recommend cycle tracking for pattern confirmation
- May indicate PNES if period correlation very high

---

### 3. 😣 Pain Level Correlation

**What It Measures:**
- Compares average pain levels on days with seizures vs. days without
- Calculates percentage of painful days that coincide with seizures
- Creates visual correlation chart over time

**Clinical Significance:**
- **High Correlation**: Suggests strong pain-seizure coupling, possibly indicating PNES or stress-related triggers
- **Moderate Correlation**: May indicate medication side effects or psychogenic component
- **Low Correlation**: Suggests seizures independent of pain/stress levels

**Interpretation:**
- Pain on seizure days >> pain on non-seizure days = Stress/anxiety may trigger seizures
- Pain levels similar both days = Pain not primary trigger factor
- Pain ALWAYS on seizure days = Strong psychogenic component

**Example Data:**
```
Avg Pain on Seizure Days: 6.2/10
Avg Pain on Non-Seizure Days: 4.1/10
Correlation: 75% (3 out of 4 pain days have seizures)
```

**Doctor Actions:**
- Screen for anxiety disorders using validated scales (GAD-7, PHQ-9)
- Refer for psychological evaluation if PNES suspected
- Consider stress management therapy (CBT, mindfulness)
- Evaluate for comorbid psychiatric conditions

---

### 4. ⏱️ Inter-Seizure Intervals

**What It Measures:**
- Time between consecutive seizures (measured in hours/days)
- Minimum, maximum, average, and median intervals
- Distribution of intervals across predefined ranges

**Clinical Significance:**
- **Very frequent** (<24h average): Severe/refractory epilepsy or cluster seizures
- **Frequent** (1-7 days): Active seizure disorder, possible need for medication adjustment
- **Infrequent** (weeks/months): Well-controlled, possible medication efficacy
- **Highly variable intervals**: May suggest PNES or environmental/stress triggers

**Interval Ranges:**
- **0-24h**: Seizures within one day (very frequent)
- **1-3d**: Seizures spaced 1-3 days apart
- **3-7d**: Weekly pattern
- **1-2w**: Bi-weekly pattern
- **2w+**: Monthly or longer intervals

**Example Data:**
```
Min Interval: 12 hours (closest seizures)
Max Interval: 14 days (longest gap)
Avg Interval: 4.2 days
Median Interval: 3 days
Distribution: Most seizures cluster 1-3 days apart
```

**Doctor Actions:**
- High variability (12h to 14d) → Consider PNES evaluation
- Consistent pattern (all 2-3 days) → May indicate cyclic trigger
- Recent decrease in intervals → Medication may need adjustment
- Long intervals → Consider medication as potentially effective

---

### 5. 📈 Seizure Duration Trend

**What It Measures:**
- Tracks individual seizure duration over time (chronologically ordered)
- Shows whether seizures are getting longer, shorter, or remaining stable
- Helps identify medication efficacy trends

**Clinical Significance:**
- **Increasing trend**: May indicate worsening condition, tolerance to medication, or stress increase
- **Decreasing trend**: May indicate medication is becoming more effective or trigger elimination
- **Stable trend**: Consistent seizure pattern, possibly well-managed
- **High variability**: Suggests environmental or stress-related triggers

**Interpretation:**
- Steep upward slope = Urgent need for medication review
- Downward slope = Current treatment may be working
- Horizontal line = Stable condition
- Sawtooth pattern = Episodic triggers, possibly PNES

**Example Data:**
```
Seizure #1: 100 seconds
Seizure #5: 88 seconds
Seizure #10: 95 seconds
Trend: Relatively stable (mean 92 seconds, slight downward trend)
```

**Doctor Actions:**
- Increasing durations → Order EEG, review medication levels
- Decreasing durations → Continue current treatment
- High variability → Consider PNES, psychological evaluation
- Trend change → Correlate with medication changes, life events

---

## Medical Insights Dashboard Interface

### Tab Navigation

The Advanced Medical Insights section uses tabbed interface for organized presentation:

1. **🍽️ Food Impact** - Food intake vs. seizure duration
2. **🩸 Menstrual Cycle** - Hormonal influence on seizures
3. **😣 Pain Correlation** - Psychological/pain triggers
4. **⏱️ Inter-Seizure Intervals** - Seizure frequency patterns
5. **📈 Duration Trend** - Temporal trend analysis (always visible)

### Visual Elements

Each insight includes:
- **Metric Cards**: Key numbers with clinical context
- **Interactive Charts**: Recharts visualizations (bar, line, pie)
- **Clinical Insights Box**: Interpretation and recommendations
- **Context Explanations**: Doctor-friendly language

---

## Data Requirements for Accurate Analysis

For comprehensive medical insights, the following data should be tracked:

### Essential Data
✅ **Seizure Records**: Date, Time, Duration
✅ **Food Intake**: Whether food was eaten before seizure
✅ **Menstrual Status**: Period/non-period designation
✅ **Pain Levels**: Daily pain documentation

### Optional but Valuable Data
📊 **Apple Watch Data**: Heart rate, sleep patterns
📊 **Emotional State**: Stress levels, anxiety indicators
📊 **Medication Timing**: When medications taken
📊 **Environmental Factors**: Sleep, caffeine, triggers

---

## API Response Structure

```json
{
  "medical_insights": {
    "food_impact": {
      "with_food_avg": 95,
      "without_food_avg": 78,
      "difference": 17,
      "food_eaters": 12,
      "non_eaters": 8,
      "trend": "longer"
    },
    "menstrual_analysis": {
      "period_avg_duration": 102,
      "non_period_avg_duration": 75,
      "difference": 27,
      "period_seizure_count": 8,
      "period_percentage": 26.7
    },
    "pain_correlation": {
      "avg_pain_seizure_days": 6.2,
      "avg_pain_non_seizure_days": 4.1,
      "days_with_pain": 8,
      "correlation_percentage": 75
    },
    "inter_seizure_intervals": {
      "min_interval": 12,
      "max_interval": 336,
      "avg_interval": 101.3,
      "median_interval": 72,
      "intervals": [48, 72, 96, 120, ...]
    }
  },
  "medical_charts": {
    "duration_trend": [
      {"seizure_number": 1, "duration": 100, "date": "2025-08-07"},
      {"seizure_number": 2, "duration": 95, "date": "2025-09-04"},
      ...
    ],
    "inter_seizure_distribution": [
      {"range": "0-24h", "count": 2},
      {"range": "1-3d", "count": 8},
      ...
    ],
    "pain_seizure_correlation": [
      {"date": "2025-08-07", "duration": 100, "pain": 5},
      ...
    ],
    "food_impact_comparison": [
      {"category": "With Food", "avg_duration": 95, "count": 12},
      {"category": "Without Food", "avg_duration": 78, "count": 8}
    ]
  }
}
```

---

## Clinical Use Cases

### Case 1: Suspected Food-Triggered Seizures
**Finding**: With food avg 120sec, without food avg 60sec (100% longer)
**Action**: 
- Recommend food diary during daily activities
- Consider elimination diet (remove common triggers: caffeine, gluten, artificial sweeteners)
- May indicate PNES triggered by anticipatory anxiety about eating
- Gastroenterology referral if GI symptoms present

### Case 2: Clear Catamenial Pattern
**Finding**: 80% of seizures occur within menstrual window; seizures 40% longer during period
**Action**:
- Confirm hormonal influence with EEG monitoring during cycle
- Discuss perimenstrual therapy options (mini-seizure prophylaxis during high-risk days)
- Refer to reproductive endocrinologist
- Consider oral contraceptives to stabilize hormones (if appropriate)

### Case 3: High Pain-Seizure Correlation
**Finding**: Avg pain 7/10 on seizure days, 3/10 on non-seizure days; 90% correlation
**Action**:
- High likelihood of PNES component
- Psychiatric evaluation priority
- Screen for trauma, anxiety, depression
- Consider psychological therapy (CBT, trauma-focused treatments)
- May not require increased epilepsy medications

### Case 4: Improving Trend
**Finding**: Seizure duration declining from 120sec to 70sec over 3 months
**Action**:
- Current medication appears effective
- Consider continuing same regimen
- Reinforce medication adherence
- Assess lifestyle changes that may be helping

---

## Recommendations by Finding

| Finding | Interpretation | Recommended Action |
|---------|-----------------|-------------------|
| Food avg 50% longer | Strong food trigger | Dietary evaluation, elimination diet |
| Food avg 50% shorter | Food protective | Encourage consistent eating patterns |
| Period seizures >>70% | Clear catamenial | Hormonal evaluation, perimenstrual prophylaxis |
| Pain correlation >75% | Psychogenic likely | Psychiatric evaluation, PNES workup |
| Pain correlation <25% | Not pain-driven | Focus on organic causes |
| Avg interval <24h | Frequent/refractory | Medication adjustment needed |
| Avg interval >30d | Well-controlled | Continue current treatment |
| Interval CV >100% | Highly variable | Consider PNES, environmental triggers |
| Duration increasing | Worsening trend | Medication review urgent |
| Duration decreasing | Improving trend | Continue current treatment |

---

## Integration with PNES Analysis

The Advanced Medical Insights complement the PNES Detection system:

- **Food Impact** + **Pain Correlation** → PNES likelihood increases if both high
- **Menstrual Pattern** → Low catamenial percentage supports PNES (if other factors present)
- **Duration Variability** → High CV supports PNES classification
- **Interval Variability** → High variability supports PNES vs. epilepsy

---

## Best Practices

### For Patients
1. ✅ Keep detailed daily logs (food, pain, stress, sleep, medication)
2. ✅ Mark menstrual cycle dates accurately
3. ✅ Note emotional events or stressors near seizures
4. ✅ Share complete dataset with doctor monthly
5. ✅ Track any medication changes

### For Doctors
1. ✅ Review insights in context of EEG findings
2. ✅ Compare metrics month-to-month for trends
3. ✅ Correlate with medication levels/adjustments
4. ✅ Order additional testing (EEG, hormonal, psychiatric) based on insights
5. ✅ Discuss findings with patient to improve compliance

---

## Limitations

⚠️ **Important Considerations**:
- Correlations shown are statistical, not causative
- Small datasets (few seizures) may show spurious patterns
- Patient self-reporting may have bias
- Doesn't replace clinical EEG monitoring
- Must be interpreted in full clinical context

---

## Future Enhancements

- Machine learning pattern detection
- Predictive risk scores for upcoming seizures
- Integration with wearable device data (heart rate, sleep, activity)
- Video analysis for semiology classification
- Medication efficacy correlation
- Genetic/comorbidity integration
- Severity scoring system

---

## References

- Epilepsy Foundation: Catamenial Epilepsy Guidelines
- American Epilepsy Society: Functional Seizure Disorders
- Functional Neurological Disorder Society: PNES Diagnostic Criteria
- International League Against Epilepsy (ILAE): Seizure Classification

---

**Version**: 1.0  
**Last Updated**: 2025  
**For**: Healthcare Providers, Researchers, and Patient Care Teams
