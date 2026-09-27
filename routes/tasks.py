"""
Task CRUD Routes Blueprint for Flask To-Do API.
Implements complete REST operations: List, Retrieve, Create, Full Update, Partial Update, Delete, and Statistics.
"""

from datetime import datetime
from flask import Blueprint, request, jsonify
from database import db
from models import Task

tasks_bp = Blueprint("tasks", __name__, url_prefix="/api/tasks")

def _parse_due_date(date_str):
    if not date_str:
        return None
    try:
        # Handles full ISO format or simple YYYY-MM-DD
        if "T" in date_str:
            return datetime.fromisoformat(date_str.replace("Z", "+00:00")).replace(tzinfo=None)
        return datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        raise ValueError(f"Invalid date format '{date_str}'. Expected ISO 8601 (e.g. 'YYYY-MM-DD' or 'YYYY-MM-DDTHH:MM:SS')")

# -------------------------------------------------------------
# GET /api/tasks - List all tasks with filter, search & pagination
# -------------------------------------------------------------
@tasks_bp.route("", methods=["GET"])
def get_tasks():
    query = Task.query

    # Filters
    status_filter = request.args.get("status")
    if status_filter:
        query = query.filter(Task.status == status_filter.lower())

    priority_filter = request.args.get("priority")
    if priority_filter:
        query = query.filter(Task.priority == priority_filter.lower())

    category_filter = request.args.get("category")
    if category_filter:
        query = query.filter(Task.category == category_filter.lower())

    # Text search in title or description
    search_query = request.args.get("q")
    if search_query:
        search_pattern = f"%{search_query}%"
        query = query.filter(
            (Task.title.ilike(search_pattern)) | (Task.description.ilike(search_pattern))
        )

    # Sorting
    sort_by = request.args.get("sort_by", "created_at").lower()
    order = request.args.get("order", "desc").lower()

    sort_columns = {
        "id": Task.id,
        "title": Task.title,
        "status": Task.status,
        "priority": Task.priority,
        "due_date": Task.due_date,
        "created_at": Task.created_at,
        "updated_at": Task.updated_at,
    }

    sort_col = sort_columns.get(sort_by, Task.created_at)
    query = query.order_by(sort_col.asc() if order == "asc" else sort_col.desc())

    # Pagination
    try:
        page = max(1, int(request.args.get("page", 1)))
        per_page = min(100, max(1, int(request.args.get("per_page", 20))))
    except ValueError:
        page, per_page = 1, 20

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        "status": "success",
        "data": [task.to_dict() for task in pagination.items],
        "pagination": {
            "page": pagination.page,
            "per_page": pagination.per_page,
            "total_items": pagination.total,
            "total_pages": pagination.pages,
            "has_next": pagination.has_next,
            "has_prev": pagination.has_prev,
        }
    }), 200

# -------------------------------------------------------------
# GET /api/tasks/<id> - Retrieve single task
# -------------------------------------------------------------
@tasks_bp.route("/<int:task_id>", methods=["GET"])
def get_task(task_id):
    task = db.session.get(Task, task_id)
    if not task:
        return jsonify({
            "status": "error",
            "message": f"Task with id {task_id} not found."
        }), 404

    return jsonify({
        "status": "success",
        "data": task.to_dict()
    }), 200

# -------------------------------------------------------------
# POST /api/tasks - Create task
# -------------------------------------------------------------
@tasks_bp.route("", methods=["POST"])
def create_task():
    if not request.is_json:
        return jsonify({"status": "error", "message": "Content-Type must be 'application/json'"}), 415

    payload = request.get_json(silent=True)
    if not payload:
        return jsonify({"status": "error", "message": "JSON body is required and cannot be empty."}), 400

    title = payload.get("title")
    if not title or not isinstance(title, str) or not title.strip():
        return jsonify({"status": "error", "message": "Field 'title' is required and must be a non-empty string."}), 400

    title = title.strip()
    if len(title) > 150:
        return jsonify({"status": "error", "message": "Field 'title' exceeds 150 characters."}), 400

    status = payload.get("status", "pending")
    if status not in Task.VALID_STATUSES:
        return jsonify({
            "status": "error",
            "message": f"Invalid status '{status}'. Allowed values: {Task.VALID_STATUSES}"
        }), 400

    priority = payload.get("priority", "medium")
    if priority not in Task.VALID_PRIORITIES:
        return jsonify({
            "status": "error",
            "message": f"Invalid priority '{priority}'. Allowed values: {Task.VALID_PRIORITIES}"
        }), 400

    due_date = None
    if "due_date" in payload and payload["due_date"]:
        try:
            due_date = _parse_due_date(payload["due_date"])
        except ValueError as e:
            return jsonify({"status": "error", "message": str(e)}), 400

    category = payload.get("category", "general")
    if category and isinstance(category, str):
        category = category.strip().lower()[:50]
    else:
        category = "general"

    description = payload.get("description", "")
    if description and isinstance(description, str):
        description = description.strip()

    new_task = Task(
        title=title,
        description=description,
        status=status,
        priority=priority,
        category=category,
        due_date=due_date
    )

    db.session.add(new_task)
    db.session.commit()

    return jsonify({
        "status": "success",
        "message": "Task created successfully.",
        "data": new_task.to_dict()
    }), 201

# -------------------------------------------------------------
# PUT /api/tasks/<id> - Full update of task
# -------------------------------------------------------------
@tasks_bp.route("/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    task = db.session.get(Task, task_id)
    if not task:
        return jsonify({"status": "error", "message": f"Task with id {task_id} not found."}), 404

    if not request.is_json:
        return jsonify({"status": "error", "message": "Content-Type must be 'application/json'"}), 415

    payload = request.get_json(silent=True)
    if not payload:
        return jsonify({"status": "error", "message": "JSON body is required."}), 400

    # In PUT, title is required
    title = payload.get("title")
    if not title or not isinstance(title, str) or not title.strip():
        return jsonify({"status": "error", "message": "Field 'title' is required for full update."}), 400

    status = payload.get("status", "pending")
    if status not in Task.VALID_STATUSES:
        return jsonify({"status": "error", "message": f"Invalid status '{status}'. Allowed: {Task.VALID_STATUSES}"}), 400

    priority = payload.get("priority", "medium")
    if priority not in Task.VALID_PRIORITIES:
        return jsonify({"status": "error", "message": f"Invalid priority '{priority}'. Allowed: {Task.VALID_PRIORITIES}"}), 400

    due_date = None
    if "due_date" in payload and payload["due_date"]:
        try:
            due_date = _parse_due_date(payload["due_date"])
        except ValueError as e:
            return jsonify({"status": "error", "message": str(e)}), 400

    task.title = title.strip()
    task.description = payload.get("description", "")
    task.status = status
    task.priority = priority
    task.category = payload.get("category", "general").strip().lower()
    task.due_date = due_date

    db.session.commit()

    return jsonify({
        "status": "success",
        "message": "Task updated successfully.",
        "data": task.to_dict()
    }), 200

# -------------------------------------------------------------
# PATCH /api/tasks/<id> - Partial update of task
# -------------------------------------------------------------
@tasks_bp.route("/<int:task_id>", methods=["PATCH"])
def patch_task(task_id):
    task = db.session.get(Task, task_id)
    if not task:
        return jsonify({"status": "error", "message": f"Task with id {task_id} not found."}), 404

    if not request.is_json:
        return jsonify({"status": "error", "message": "Content-Type must be 'application/json'"}), 415

    payload = request.get_json(silent=True)
    if not payload:
        return jsonify({"status": "error", "message": "JSON body is required."}), 400

    if "title" in payload:
        title = payload["title"]
        if not title or not isinstance(title, str) or not title.strip():
            return jsonify({"status": "error", "message": "Title cannot be empty."}), 400
        task.title = title.strip()

    if "description" in payload:
        task.description = payload["description"]

    if "status" in payload:
        status = payload["status"]
        if status not in Task.VALID_STATUSES:
            return jsonify({"status": "error", "message": f"Invalid status '{status}'. Allowed: {Task.VALID_STATUSES}"}), 400
        task.status = status

    if "priority" in payload:
        priority = payload["priority"]
        if priority not in Task.VALID_PRIORITIES:
            return jsonify({"status": "error", "message": f"Invalid priority '{priority}'. Allowed: {Task.VALID_PRIORITIES}"}), 400
        task.priority = priority

    if "category" in payload:
        task.category = str(payload["category"]).strip().lower()[:50]

    if "due_date" in payload:
        if payload["due_date"] is None:
            task.due_date = None
        else:
            try:
                task.due_date = _parse_due_date(payload["due_date"])
            except ValueError as e:
                return jsonify({"status": "error", "message": str(e)}), 400

    db.session.commit()

    return jsonify({
        "status": "success",
        "message": "Task modified successfully.",
        "data": task.to_dict()
    }), 200

# -------------------------------------------------------------
# DELETE /api/tasks/<id> - Delete task
# -------------------------------------------------------------
@tasks_bp.route("/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    task = db.session.get(Task, task_id)
    if not task:
        return jsonify({"status": "error", "message": f"Task with id {task_id} not found."}), 404

    db.session.delete(task)
    db.session.commit()

    return jsonify({
        "status": "success",
        "message": f"Task with id {task_id} deleted successfully."
    }), 200

# -------------------------------------------------------------
# GET /api/tasks/stats - Task aggregation statistics
# -------------------------------------------------------------
@tasks_bp.route("/stats", methods=["GET"])
def get_task_stats():
    total_tasks = Task.query.count()
    status_counts = {}
    for st in Task.VALID_STATUSES:
        status_counts[st] = Task.query.filter_by(status=st).count()

    priority_counts = {}
    for pr in Task.VALID_PRIORITIES:
        priority_counts[pr] = Task.query.filter_by(priority=pr).count()

    now = datetime.utcnow()
    overdue_count = Task.query.filter(
        Task.due_date < now,
        Task.status.notin_(["completed", "cancelled"])
    ).count()

    return jsonify({
        "status": "success",
        "total": total_tasks,
        "by_status": status_counts,
        "by_priority": priority_counts,
        "overdue_tasks": overdue_count
    }), 200
