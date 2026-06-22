# Data Setup Guide for CycloneOPS PRO

## Overview

CycloneOPS PRO requires historical cyclone meteorological data for training and predictions. This guide explains how to obtain and prepare the data.

## Data Sources

### 1. **Official IMD Data** (Recommended)
- **Source**: [India Meteorological Department RSMC](https://rsmcnewdelhi.imd.gov.in/)
- **Format**: CSV or Excel spreadsheets
- **Frequency**: Updated after each cyclone season
- **License**: Public domain/Government of India

#### Steps to download:
1. Visit the RSMC website
2. Navigate to "Past Cyclones" or "Historical Data" section
3. Select the desired year/season
4. Download in CSV or Excel format
5. Save to `data/raw/` directory

### 2. **Sample Data** (Testing)
A sample dataset with 629 records is included in the project:
```
data/raw/New_Data.csv
```

This can be used for:
- Testing the training pipeline
- Validating the web dashboard
- Demonstration purposes

### 3. **Generate Test Data**
Create synthetic data for development:
```bash
python make_test_data.py
```

This will generate random but realistic cyclone records.

---

## Data Format

Your CSV file must contain the following columns (exact names):

| Column | Description | Unit | Range | Example |
|--------|-------------|------|-------|---------|
| `Date` or `date` | Observation date | YYYY-MM-DD | Any | 2021-05-15 |
| `Time_UTC` or `time` | Observation time | HH:MM UTC | 00:00-23:59 | 12:00 |
| `Latitude` or `lat` | Storm center latitude | °N | -90 to +90 | 12.5 |
| `Longitude` or `lon` | Storm center longitude | °E | -180 to +180 | 75.3 |
| `CI_No` or `ci` | Dvorak CI number | - | 1.0-8.0 | 4.5 |
| `ECP_hPa` or `ecp` | Eye center pressure | hPa | 850-1020 | 920 |
| `dP_hPa` or `dp` | Pressure drop | hPa | 0-200 | 80 |
| `MSW_kt` or `msw` | Max sustained wind speed | knots | 0-150 | 65 |
| `Category` or `cat` | IMD cyclone category | - | D, DD, CS, SCS, VSCS, ESCS | SCS |

### Supported Category Codes:
- **D**: Depression
- **DD**: Deep Depression
- **CS**: Cyclonic Storm
- **SCS**: Severe Cyclonic Storm
- **VSCS**: Very Severe Cyclonic Storm
- **ESCS**: Extremely Severe Cyclonic Storm

---

## Data Upload & Processing

### Method 1: Web Dashboard
1. Start the app: `python app/main.py`
2. Login with credentials (admin/cyclone123)
3. Click "📂 Upload CSV" in navbar
4. Select your CSV file
5. Data is automatically processed and saved

### Method 2: Manual Processing
```bash
# 1. Place CSV in data/raw/
cp your_data.csv data/raw/New_Data.csv

# 2. Fix column names (if needed)
python fix_wind.py

# 3. Train model with new data
python core/train.py
```

### Method 3: Programmatic
```python
from core.dataset import load_raw, clean, save_processed

# Load and clean
df = load_raw()  # Automatically maps column names
df_clean = clean(df)

# Inspect
print(f"Records: {len(df_clean)}")
print(f"Features: {df_clean.columns.tolist()}")

# Save
save_processed(df_clean)
```

---

## Data Validation

The system automatically validates data:

✅ **Column names** are mapped automatically (case-insensitive)  
✅ **Data types** are converted (strings → float/int as needed)  
✅ **Missing values** are handled:
  - Required fields dropped if null
  - CI_No filled with median
  - dP_hPa filled with 0
✅ **Invalid categories** are filtered  
✅ **Range validation** ensures realistic values

---

## Quality Checks

After uploading, verify your data:

```python
from core.dataset import load_processed, get_stats

df = load_processed()
stats = get_stats(df)

print(f"Total records: {stats['total_rows']}")
print(f"Date range: {stats['date_range']}")
print(f"Categories: {stats['categories']}")
print(f"Missing values: {df.isnull().sum()}")
```

Expected output:
```
Total records: 629
Date range: 2000-01-01 to 2025-12-31
Categories: {'D': 120, 'DD': 150, 'CS': 180, 'SCS': 120, 'VSCS': 50, 'ESCS': 9}
Missing values: Date          0
               Latitude       0
               ...
```

---

## Training with New Data

Once data is loaded and validated:

```bash
# Train the model
python core/train.py

# Or via API
curl -X POST http://localhost:5000/api/train \
  -H "Content-Type: application/json" \
  -d '{"epochs": 200, "lr": 0.0005}'
```

Monitor training progress in console output.

---

## Common Issues & Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| **CSV not found** | File path incorrect | Check `data/raw/` directory exists |
| **Column name error** | Unexpected column names | Run `python fix_wind.py` or rename manually |
| **Type conversion error** | Non-numeric data in numeric column | Clean data: remove commas, check for text |
| **Category not recognized** | Invalid IMD category | Use only: D, DD, CS, SCS, VSCS, ESCS |
| **Few records** | Insufficient data | Model needs 100+ records minimum for training |
| **Low accuracy** | Poor data quality | Review data distribution, check for outliers |

---

## Data Privacy & Security

⚠️ **Important Considerations:**
- Data is stored locally in `data/raw/` and `data/processed/`
- No data is sent to external servers
- Ensure `data/` is included in `.gitignore` (already configured)
- For production, use environment-specific data paths
- Sanitize user-uploaded files before processing

---

## Example: Complete Workflow

```bash
# 1. Download data from IMD
# Save as: data/raw/IMD_2025_Data.csv

# 2. Copy to expected location
cp data/raw/IMD_2025_Data.csv data/raw/New_Data.csv

# 3. Fix column names
python fix_wind.py

# 4. Verify data loads
python -c "from core.dataset import load_raw; df = load_raw(); print(f'Loaded {len(df)} records')"

# 5. Train model
python core/train.py

# 6. Start app and test
python app/main.py
# Open http://localhost:5000 in browser
```

---

## Reference: DataFrame Structure

After processing, the DataFrame contains:

```python
import pandas as pd
from core.dataset import load_processed

df = load_processed()
df.info()  # Shows all columns and types

# Output:
# Column       Non-Null Count  Dtype  
# --------     ----           -----
# Date         629 non-null    object
# Time_UTC     629 non-null    object
# Latitude     629 non-null    float64
# Longitude    629 non-null    float64
# CI_No        629 non-null    float64
# ECP_hPa      629 non-null    float64
# dP_hPa       629 non-null    float64
# MSW_kt       629 non-null    float64
# Category     629 non-null    object (categories: D, DD, CS, SCS, VSCS, ESCS)
```

---

**Last Updated:** 2026-06-22  
**Version:** 1.0
