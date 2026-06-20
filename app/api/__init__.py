from flask import Blueprint, request, jsonify, session
import os, sys, io

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.config  import Config
from core.dataset import load_raw, clean, save_processed, get_stats, to_geojson
from core.model   import get_model

api = Blueprint("api", __name__, url_prefix="/api")


def need_login():
    if not session.get("user"):
        return jsonify({"error": "Not authenticated"}), 401
    return None


# ── /api/status ──────────────────────────────────────────────
@api.route("/status")
def status():
    m = get_model()
    return jsonify({
        "model_ready"   : m.is_ready(),
        "model_type"    : "PyTorch CycloneNet",
        "training_data" : os.path.exists(Config.DATA_PROCESSED),
    })


# ── /api/train ───────────────────────────────────────────────
@api.route("/train", methods=["POST"])
def train_model():
    guard = need_login()
    if guard: return guard
    try:
        data   = request.get_json(silent=True) or {}
        epochs = int(data.get("epochs", Config.EPOCHS))
        lr     = float(data.get("lr",     Config.LR))

        from core.train import train as run_train
        run_train(epochs=epochs, lr=lr)

        # Reload singleton
        import core.model as cm
        cm._instance = None
        m = get_model()
        return jsonify({"success": True,
                        "message": f"CycloneNet trained — epochs={epochs}"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── /api/predict ─────────────────────────────────────────────
@api.route("/predict", methods=["POST"])
def predict():
    guard = need_login()
    if guard: return guard
    try:
        d   = request.get_json()
        lat = float(d["lat"])
        lon = float(d["lon"])
        ci  = float(d.get("ci", 2.5))
        ecp = float(d["ecp"])
        dp  = float(d["dp"])
        msw = float(d["msw"])

        m = get_model()
        if not m.is_ready():
            return jsonify({"error": "Model not trained. POST /api/train first."}), 400

        result = m.predict_one(lat, lon, ci, ecp, dp, msw)
        return jsonify(result)
    except KeyError as e:
        return jsonify({"error": f"Missing field: {e}"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── /api/data ────────────────────────────────────────────────
@api.route("/data")
def get_data():
    guard = need_login()
    if guard: return guard
    try:
        from core.dataset import load_processed
        df = load_processed()
        return jsonify({
            "geojson": to_geojson(df),
            "stats"  : get_stats(df),
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── /api/upload ──────────────────────────────────────────────
@api.route("/upload", methods=["POST"])
def upload_csv():
    guard = need_login()
    if guard: return guard
    if "file" not in request.files:
        return jsonify({"error": "No file"}), 400
    f = request.files["file"]
    if not f.filename.endswith(".csv"):
        return jsonify({"error": "Only CSV files allowed"}), 400
    try:
        import pandas as pd
        df_new = pd.read_csv(io.StringIO(f.read().decode("utf-8")))
        os.makedirs(os.path.dirname(Config.DATA_RAW), exist_ok=True)
        df_new.to_csv(Config.DATA_RAW, index=False)
        df_clean = clean(load_raw())
        save_processed(df_clean)
        return jsonify({"success": True, "rows": len(df_clean),
                        "message": f"Uploaded & processed {len(df_clean)} records"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── /api/scan ────────────────────────────────────────────────
@api.route("/scan")
def api_scan():
    guard = need_login()
    if guard: return guard
    return jsonify({
        "active_systems": [],
        "message"       : "No active cyclone systems detected",
        "source"        : "IMD RSMC (simulated)"
    })
