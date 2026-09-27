"""
Health check and database telemetry blueprint.
"""

import time
import os
import psutil
from datetime import datetime
from flask import Blueprint, jsonify, current_app
from sqlalchemy import text
from database import db

health_bp = Blueprint("health", __name__)
BOOT_TIME = time.time()

@health_bp.route("/health", methods=["GET"])
def health_check():
    db_connected = False
    db_error = None
    dialect = "unknown"

    try:
        with db.engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        db_connected = True
        dialect = db.engine.dialect.name
    except Exception as e:
        db_error = str(e)

    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()

    return jsonify({
        "status": "healthy" if db_connected else "degraded",
        "service": "Flask To-Do REST API",
        "uptime_seconds": round(time.time() - BOOT_TIME, 2),
        "database": {
            "connected": db_connected,
            "engine": dialect,
            "error": db_error
        },
        "system": {
            "memory_rss_mb": round(memory_info.rss / (1024 * 1024), 2),
            "cpu_percent": psutil.cpu_percent(interval=None)
        },
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }), 200 if db_connected else 503
