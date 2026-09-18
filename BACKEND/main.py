import os
import sys
from flask import Flask, jsonify

# Ensure BACKEND root is in python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from api.chat import chat_bp
from api.auth import auth_bp
from db.connection import check_db_connection

app = Flask(__name__)
app.register_blueprint(chat_bp)
app.register_blueprint(auth_bp)

@app.route("/", methods=["GET"])
def index():
    return jsonify({
        "status": "online",
        "service": "Arudhra Mobile Stores RAG AI Shopping Assistant API",
        "location": "Pithapuram, AP, India",
        "version": "1.0.0"
    }), 200

@app.route("/health", methods=["GET"])
def health_check():
    db_healthy = check_db_connection()
    status_code = 200 if db_healthy else 500
    return jsonify({
        "status": "healthy" if db_healthy else "unhealthy",
        "database": "connected" if db_healthy else "disconnected"
    }), status_code

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    print(f"[INFO] Starting Arudhra RAG Assistant Server on port {port}...")
    app.run(host="0.0.0.0", port=port, debug=True)
