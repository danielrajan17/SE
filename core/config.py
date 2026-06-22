import os
import logging

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Configure logging
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
LOG_DIR = os.path.join(BASE_DIR, 'logs')
os.makedirs(LOG_DIR, exist_ok=True)

# Configure root logger
logging.basicConfig(
    level=LOG_LEVEL,
    format=LOG_FORMAT,
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, 'app.log')),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "cyclone-secret-2025")
    DEBUG = True

    # Paths
    DATA_RAW       = os.path.join(BASE_DIR, "data", "raw",       "New_Data.csv")
    DATA_PROCESSED = os.path.join(BASE_DIR, "data", "processed", "clean_data.csv")
    MODEL_DIR      = os.path.join(BASE_DIR, "saved_models")
    MODEL_PATH     = os.path.join(BASE_DIR, "saved_models", "cyclone_net.pt")
    SCALER_PATH    = os.path.join(BASE_DIR, "saved_models", "scaler.joblib")
    ENCODER_PATH   = os.path.join(BASE_DIR, "saved_models", "label_encoder.joblib")

    # PyTorch Model
    FEATURES    = ["Latitude", "Longitude", "CI_No", "ECP_hPa", "dP_hPa", "MSW_kt"]
    TARGET      = "Category"
    INPUT_SIZE  = 6
    HIDDEN_SIZES= [128, 256, 128]   # Wider network
    DROPOUT     = 0.4  # Increased dropout
    EPOCHS      = 100  # More epochs
    LR          = 0.0005  # Lower LR
    BATCH_SIZE  = 16  # Smaller batch
    WEIGHT_DECAY = 1e-4
    WEIGHT_DECAY = 1e-4

    # IMD Category map (ordered)
    CATEGORIES  = ["D", "DD", "CS", "SCS", "VSCS", "ESCS"]
    CATEGORY_INFO = {
        "D"    : {"name": "Depression",                "color": "#64b5f6", "order": 0, "risk": "LOW"},
        "DD"   : {"name": "Deep Depression",            "color": "#4dd0e1", "order": 1, "risk": "LOW"},
        "CS"   : {"name": "Cyclonic Storm",             "color": "#ffe44d", "order": 2, "risk": "MEDIUM"},
        "SCS"  : {"name": "Severe Cyclonic Storm",      "color": "#ffb74d", "order": 3, "risk": "HIGH"},
        "VSCS" : {"name": "Very Severe Cyclonic Storm", "color": "#ff7043", "order": 4, "risk": "VERY HIGH"},
        "ESCS" : {"name": "Extremely Severe CS",        "color": "#ff4b6e", "order": 5, "risk": "EXTREME"},
    }

    # Login
    USERS = {
        "admin": "cyclone123",
        "user":  "test123"
    }
