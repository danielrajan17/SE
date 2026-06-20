"""
CycloneOPS PRO — Flask Entry Point

Run:
    python app/main.py
Then open: http://127.0.0.1:5000
"""

import os
import sys

# Make root importable
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from flask import (
    Flask, render_template, request,
    redirect, url_for, session, jsonify
)
from core.config import Config

app = Flask(
    __name__,
    template_folder = "templates",
    static_folder   = "static",
)
app.secret_key = Config.SECRET_KEY

# Register API blueprint
from app.api import api
app.register_blueprint(api)

# --- DISABLE CACHE IN DEVELOPMENT ---
@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response

# ── Auth routes ─────────────────────────────────────────────
@app.route("/", methods=["GET"])
def index():
    if session.get("user"):
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        if Config.USERS.get(username) == password:
            session["user"] = username
            return redirect(url_for("dashboard"))
        error = "Invalid username or password"
    return render_template("login.html", error=error)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# ── Dashboard ───────────────────────────────────────────────
@app.route("/dashboard")
def dashboard():
    if not session.get("user"):
        return redirect(url_for("login"))
    return render_template(
        "dashboard.html",
        user          = session["user"],
        category_info = Config.CATEGORY_INFO,
    )


# ── Run ─────────────────────────────────────────────────────
if __name__ == "__main__":
    # Auto-train if model not found
    from core.model import get_model
    m = get_model()
    if not m.is_ready():
        print("[main] No saved model found — training now...")
        try:
            from core.train import train
            train()
            m.load()
        except Exception as e:
            print(f"[main] Could not auto-train: {e}")
            print("[main] Run manually: python core/train.py")

    app.run(host="127.0.0.1", port=5000, debug=Config.DEBUG)