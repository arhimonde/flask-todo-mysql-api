"""
Flask REST API for Task Management (To-Do List) with MySQL & SQLAlchemy.
Demonstrates standard CRUD pattern, filtering, pagination, statistics, and health checks.
"""

import os
from flask import Flask, jsonify
from config import Config
from database import init_db
from routes.tasks import tasks_bp
from routes.health import health_bp

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize Database & verify connection / tables
    init_db(app)

    # Register Blueprints
    app.register_blueprint(tasks_bp)
    app.register_blueprint(health_bp)

    # CORS Headers middleware
    @app.after_request
    def set_cors(response):
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        return response

    # Error Handlers
    @app.errorhandler(400)
    def handle_bad_request(e):
        return jsonify({"status": "error", "code": 400, "message": getattr(e, "description", "Bad Request")}), 400

    @app.errorhandler(404)
    def handle_not_found(e):
        return jsonify({"status": "error", "code": 404, "message": "Resource or endpoint not found."}), 404

    @app.errorhandler(405)
    def handle_method_not_allowed(e):
        return jsonify({"status": "error", "code": 405, "message": "Method Not Allowed for this route."}), 405

    @app.errorhandler(415)
    def handle_unsupported_media_type(e):
        return jsonify({"status": "error", "code": 415, "message": "Content-Type must be application/json."}), 415

    @app.errorhandler(500)
    def handle_internal_error(e):
        return jsonify({"status": "error", "code": 500, "message": "Internal Server Error."}), 500

    # API Documentation Index
    @app.route("/", methods=["GET"])
    def index():
        return jsonify({
            "service": "Flask MySQL To-Do REST API",
            "version": "1.0.0",
            "description": "Production-grade RESTful API for task management with full CRUD and MySQL support",
            "endpoints": {
                "GET /api/tasks": "List tasks (supports ?status=, ?priority=, ?category=, ?q=, ?page=, ?per_page=, ?sort_by=)",
                "GET /api/tasks/<id>": "Retrieve a single task by ID",
                "POST /api/tasks": "Create a new task (JSON payload)",
                "PUT /api/tasks/<id>": "Replace/full update of a task",
                "PATCH /api/tasks/<id>": "Partial update of a task (e.g. status, title)",
                "DELETE /api/tasks/<id>": "Delete a task by ID",
                "GET /api/tasks/stats": "Task aggregation metrics (total, by status, overdue)",
                "GET /health": "Health and database status"
            },
            "sample_create_payload": {
                "title": "Configure MySQL cluster backup",
                "description": "Set up automated mysqldump cron with S3 offsite replication",
                "priority": "high",
                "status": "pending",
                "category": "devops",
                "due_date": "2026-10-15T18:00:00"
            }
        }), 200

    return app

app = create_app()

if __name__ == "__main__":
    host = os.environ.get("FLASK_HOST", "0.0.0.0")
    port = int(os.environ.get("FLASK_PORT", 5002))
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"

    print("=" * 65)
    print(f" 📋 Starting To-Do REST API on http://{host}:{port}")
    print("=" * 65)
    app.run(host=host, port=port, debug=debug)
