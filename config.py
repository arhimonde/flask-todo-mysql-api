"""
Configuration module for Flask To-Do MySQL REST API.
Handles database URIs, environment variables, and fallback settings.
"""

import os
import socket
from urllib.parse import urlparse
from dotenv import load_dotenv

load_dotenv()

def is_mysql_reachable(host, port, timeout=1.0):
    """Quick socket check to verify if MySQL port is open and listening."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, int(port)))
        sock.close()
        return result == 0
    except Exception:
        return False

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")
    
    MYSQL_HOST = os.environ.get("MYSQL_HOST", "localhost")
    MYSQL_PORT = int(os.environ.get("MYSQL_PORT", 3306))
    MYSQL_USER = os.environ.get("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD", "")
    MYSQL_DB = os.environ.get("MYSQL_DB", "todo_db")
    
    DEFAULT_MYSQL_URI = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"
    SQLITE_PATH = os.path.join(os.path.dirname(__file__), "tasks.db")
    SQLITE_FALLBACK_URI = f"sqlite:///{SQLITE_PATH}"

    USE_SQLITE = os.environ.get("USE_SQLITE", "").lower() in ("true", "1", "yes")

    # Resolve database URI:
    # 1. If explicit SQLALCHEMY_DATABASE_URI / DATABASE_URL is set, use it.
    # 2. If USE_SQLITE is requested, use SQLite.
    # 3. Otherwise, check if MySQL is running on host:port. If yes, use MySQL; if not, use SQLite fallback.
    if os.environ.get("DATABASE_URL"):
        SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    elif USE_SQLITE:
        SQLALCHEMY_DATABASE_URI = SQLITE_FALLBACK_URI
    else:
        if is_mysql_reachable(MYSQL_HOST, MYSQL_PORT):
            SQLALCHEMY_DATABASE_URI = DEFAULT_MYSQL_URI
        else:
            SQLALCHEMY_DATABASE_URI = SQLITE_FALLBACK_URI

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_recycle": 280,
        "pool_pre_ping": True,
    }

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"

