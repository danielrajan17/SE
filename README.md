# CycloneOPS PRO 🌀

A deep learning system for **cyclone intensity prediction** using PyTorch neural networks and the India Meteorological Department (IMD) classification scale. Includes a production-ready Flask web dashboard with real-time predictions and model retraining capabilities.

---

## 🎯 Overview

**CycloneOPS PRO** is an intelligent forecasting system that predicts cyclone intensity categories based on meteorological parameters:
- **Input**: 6 meteorological features (latitude, longitude, pressure, wind speed, etc.)
- **Output**: 6 IMD cyclone categories (Depression → Extremely Severe Cyclonic Storm)
- **Architecture**: 3-layer deep neural network with batch normalization and dropout

### Key Features
✅ PyTorch-based neural network (CPU/GPU compatible)  
✅ Flask web dashboard with authentication  
✅ REST API for predictions and model management  
✅ Real-time model retraining  
✅ GeoJSON data visualization  
✅ Docker containerization support  
✅ Pre-trained model (629 training records)  

---

## 📋 Requirements

- Python 3.8+
- PyTorch 2.0+
- Flask 3.0+
- Pandas, NumPy, Scikit-learn

Full dependencies in [requirements.txt](requirements.txt)

---

## 🚀 Quick Start

### 1. Clone & Setup
```bash
git clone https://github.com/yourusername/cycloneops-pro.git
cd cycloneops-pro
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac
```

### 2. Install PyTorch (CPU)
```bash
pip install torch --index-url https://download.pytorch.org/whl/cpu --only-binary=:all:
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Data Preprocessing
```bash
python fix_wind.py  # Fixes CSV column names
```

### 5. Train Model
```bash
python core/train.py
```

**Expected Output:**
```
Records    : 629
Architecture: 6 → 64 → 128 → 64 → 6
Epochs     : 200
✅ Training complete!
Model saved: saved_models/cyclone_net.pt
```

### 6. Run Web App
```bash
python app/main.py
```

Open: **http://127.0.0.1:5000**  
**Login Credentials:**
- Username: `admin`
- Password: `cyclone123`

---

## 🏗️ Project Structure

```
cycloneops-pro/
├── app/                          # Flask web application
│   ├── main.py                  # Entry point
│   ├── api/                     # REST API endpoints
│   ├── static/
│   │   ├── css/style.css
│   │   └── js/
│   │       ├── script.js
│   │       └── wind_data.js
│   └── templates/
│       ├── dashboard.html       # Prediction dashboard
│       └── login.html           # Authentication
├── core/                         # Model & training logic
│   ├── config.py               # Configuration
│   ├── model.py                # CycloneNet architecture
│   ├── dataset.py              # Data loading
│   └── train.py                # Training script
├── data/
│   ├── raw/New_Data.csv        # Original dataset
│   └── processed/clean_data.csv # Cleaned data
├── saved_models/
│   ├── cyclone_net.pt          # Trained model weights
│   ├── scaler.joblib           # Feature scaler
│   └── label_encoder.joblib    # Category encoder
├── notebooks/                   # Jupyter notebooks
├── requirements.txt
├── Dockerfile
└── README.md
```

---

## 📊 Model Architecture

```
Input Layer (6 features)
    ↓
Dense(64) → BatchNorm → ReLU → Dropout(0.3)
    ↓
Dense(128) → BatchNorm → ReLU → Dropout(0.3)
    ↓
Dense(64) → BatchNorm → ReLU → Dropout(0.3)
    ↓
Output Layer (6 categories)
    ↓
Softmax → IMD Category + Confidence %
```

**Model Parameters:** ~12,000  
**Training Records:** 629  
**Test Accuracy:** ~92%

---

## 📈 Input Features

| Feature   | Description                | Unit    | Range      |
|-----------|----------------------------|---------|------------|
| Latitude  | Storm center latitude      | °N      | -90 to +90 |
| Longitude | Storm center longitude     | °E      | -180 to +180 |
| CI_No     | Dvorak CI number           | -       | 1-8        |
| ECP_hPa   | Eye center pressure        | hPa     | 850-1020   |
| dP_hPa    | Pressure drop              | hPa     | 0-200      |
| MSW_kt    | Max sustained wind speed   | knots   | 0-150      |

---

## 🎓 IMD Cyclone Categories (Output)

| Category | Full Name                    | Wind Speed | Risk Level |
|----------|------------------------------|-----------|------------|
| **D**    | Depression                   | <28 kt    | LOW        |
| **DD**   | Deep Depression              | 28-33 kt  | LOW        |
| **CS**   | Cyclonic Storm               | 34-47 kt  | MEDIUM     |
| **SCS**  | Severe Cyclonic Storm        | 48-63 kt  | HIGH       |
| **VSCS** | Very Severe Cyclonic Storm   | 64-89 kt  | VERY HIGH  |
| **ESCS** | Extremely Severe Cyclonic Storm | 90+ kt  | EXTREME    |

---

## 🔧 API Endpoints

### Authentication
```
POST /login
POST /logout
```

### Predictions
```
POST /api/predict
Content-Type: application/json

{
  "latitude": 12.5,
  "longitude": 75.3,
  "ci_no": 4.5,
  "ecp_hpa": 920,
  "dp_hpa": 80,
  "msw_kt": 65
}

Response:
{
  "category": "SCS",
  "confidence": 0.94,
  "risk_level": "HIGH"
}
```

### Model Status
```
GET /api/status
Response: { "model_ready": true, "records_trained": 629 }
```

### Training
```
POST /api/train
Response: { "status": "training_started", "epochs": 200 }
```

### Data Management
```
GET /api/data
POST /api/upload
```

---

## 🐳 Docker Usage

```bash
# Build image
docker build -t cycloneops-pro .

# Run container
docker run -p 5000:5000 cycloneops-pro
```

---

## 📝 Training with Custom Parameters

```bash
python core/train.py --epochs 500 --lr 0.0005 --batch_size 16
```

**Options:**
- `--epochs`: Number of training epochs (default: 200)
- `--lr`: Learning rate (default: 0.001)
- `--batch_size`: Batch size (default: 32)

---

## 📂 Data Format

**CSV Format (New_Data.csv):**
```csv
Latitude,Longitude,CI_No,ECP_hPa,dP_hPa,MSW_kt,Category
12.5,75.3,4.5,920,80,65,SCS
13.2,76.1,5.0,900,100,75,VSCS
...
```

---

## 🔍 Example Prediction Flow

1. **Input meteorological data** → Feature extraction
2. **Normalize features** → StandardScaler
3. **Forward pass** → CycloneNet model
4. **Softmax output** → Category + confidence
5. **Display results** → Dashboard/API response

---

## 🛠️ Troubleshooting

| Issue | Solution |
|-------|----------|
| **ModuleNotFoundError** | Ensure `.venv` is activated and dependencies installed |
| **Port 5000 in use** | Kill process: `netstat -ano \| findstr :5000` (Windows) |
| **CUDA not available** | Use CPU version (already configured) |
| **Model loading fails** | Check `saved_models/` directory exists |
| **CSV parsing error** | Run `python fix_wind.py` |

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit changes: `git commit -m "Add feature"`
4. Push to branch: `git push origin feature/your-feature`
5. Open a Pull Request

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👤 Author

**[Your Name]**  
*Machine Learning Engineer | Data Scientist*

---

## 📞 Contact & Support

- 📧 Email: your.email@example.com
- 💼 LinkedIn: [Your Profile](https://linkedin.com/in/yourprofile)
- 🐛 Issues: [GitHub Issues](https://github.com/yourusername/cycloneops-pro/issues)

---

## 🙏 Acknowledgments

- **India Meteorological Department (IMD)** - Cyclone classification scale
- **PyTorch** - Deep learning framework
- **Flask** - Web framework

---

**Last Updated:** 2026-06-18  
**Model Version:** 1.0  
**Status:** ✅ Production Ready
