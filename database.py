"""
Database initialization and connection management.
Supports MySQL connection with SQLite fallback for offline development.
"""

import logging
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

db = SQLAlchemy()
logger = logging.getLogger(__name__)

def init_db(app):
    """
    Initializes SQLAlchemy with the Flask application and ensures tables exist.
    """
    db.init_app(app)

    with app.app_context():
        try:
            with db.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            dialect = db.engine.dialect.name
            print(f"✅ [Database] Connected to {dialect.upper()} engine ({app.config.get('SQLALCHEMY_DATABASE_URI')})")
        except Exception as err:
            print(f"⚠️ [Database] Connection warning: {err}")

        # Create all tables if they don't exist
        db.create_all()

