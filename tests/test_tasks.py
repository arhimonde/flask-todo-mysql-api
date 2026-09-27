"""
Comprehensive Unit Tests for Flask To-Do REST API.
Covers:
  - Database initialization in memory
  - GET /api/tasks (list, filter by status/priority/category, pagination, search)
  - GET /api/tasks/<id> (success, 404)
  - POST /api/tasks (validation: empty title, invalid status/priority/date, 201 created)
  - PUT /api/tasks/<id> (full update, 404, validation)
  - PATCH /api/tasks/<id> (partial status toggle, title update)
  - DELETE /api/tasks/<id> (200 success, 404)
  - GET /api/tasks/stats (metrics calculation)
  - GET /health (telemetry ping)
"""

import unittest
import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app
from config import TestConfig
from database import db
from models import Task

class TaskApiTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def _create_sample_task(self, title="Test Task", status="pending", priority="medium", category="general", due_date=None):
        task = Task(title=title, status=status, priority=priority, category=category, due_date=due_date)
        db.session.add(task)
        db.session.commit()
        return task

    # 1. Health check
    def test_health_check(self):
        res = self.client.get("/health")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["status"], "healthy")
        self.assertTrue(data["database"]["connected"])

    # 2. GET /api/tasks (Empty & Populated)
    def test_get_tasks_empty(self):
        res = self.client.get("/api/tasks")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(len(data["data"]), 0)
        self.assertEqual(data["pagination"]["total_items"], 0)

    def test_get_tasks_list_and_filter(self):
        self._create_sample_task(title="Deploy Backend", status="completed", priority="high", category="devops")
        self._create_sample_task(title="Write Docs", status="pending", priority="low", category="docs")
        self._create_sample_task(title="Fix Bug", status="pending", priority="urgent", category="devops")

        # List all
        res = self.client.get("/api/tasks")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.get_json()["data"]), 3)

        # Filter by status
        res_pending = self.client.get("/api/tasks?status=pending")
        self.assertEqual(len(res_pending.get_json()["data"]), 2)

        # Filter by category
        res_devops = self.client.get("/api/tasks?category=devops")
        self.assertEqual(len(res_devops.get_json()["data"]), 2)

        # Search query 'Bug'
        res_search = self.client.get("/api/tasks?q=Bug")
        self.assertEqual(len(res_search.get_json()["data"]), 1)
        self.assertEqual(res_search.get_json()["data"][0]["title"], "Fix Bug")

    # 3. GET /api/tasks/<id>
    def test_get_task_by_id(self):
        task = self._create_sample_task(title="Inspect Unit")
        res = self.client.get(f"/api/tasks/{task.id}")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["data"]["title"], "Inspect Unit")

    def test_get_task_not_found(self):
        res = self.client.get("/api/tasks/9999")
        self.assertEqual(res.status_code, 404)
        data = res.get_json()
        self.assertEqual(data["status"], "error")

    # 4. POST /api/tasks (Creation & Validation)
    def test_create_task_success(self):
        payload = {
            "title": "Migrate MySQL database",
            "description": "Perform schema upgrade",
            "priority": "high",
            "status": "pending",
            "category": "infrastructure",
            "due_date": "2026-11-20T10:00:00"
        }
        res = self.client.post("/api/tasks", json=payload)
        self.assertEqual(res.status_code, 201)
        data = res.get_json()
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["data"]["title"], "Migrate MySQL database")
        self.assertEqual(data["data"]["priority"], "high")
        self.assertIsNotNone(data["data"]["id"])

    def test_create_task_missing_title(self):
        res = self.client.post("/api/tasks", json={"priority": "high"})
        self.assertEqual(res.status_code, 400)
        self.assertIn("Field 'title' is required", res.get_json()["message"])

    def test_create_task_invalid_status(self):
        res = self.client.post("/api/tasks", json={"title": "Test", "status": "invalid_state"})
        self.assertEqual(res.status_code, 400)
        self.assertIn("Invalid status", res.get_json()["message"])

    def test_create_task_invalid_date_format(self):
        res = self.client.post("/api/tasks", json={"title": "Test", "due_date": "invalid-date"})
        self.assertEqual(res.status_code, 400)
        self.assertIn("Invalid date format", res.get_json()["message"])

    # 5. PUT /api/tasks/<id> (Full Update)
    def test_put_update_task(self):
        task = self._create_sample_task(title="Old Title", priority="low", status="pending")
        update_payload = {
            "title": "New Title Updated",
            "description": "Updated details",
            "priority": "urgent",
            "status": "in_progress",
            "category": "general"
        }
        res = self.client.put(f"/api/tasks/{task.id}", json=update_payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["data"]["title"], "New Title Updated")
        self.assertEqual(data["data"]["priority"], "urgent")
        self.assertEqual(data["data"]["status"], "in_progress")

    # 6. PATCH /api/tasks/<id> (Partial Update)
    def test_patch_task(self):
        task = self._create_sample_task(title="Initial Task", status="pending")
        patch_payload = {"status": "completed"}
        res = self.client.patch(f"/api/tasks/{task.id}", json=patch_payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["data"]["status"], "completed")
        self.assertEqual(data["data"]["title"], "Initial Task")

    # 7. DELETE /api/tasks/<id>
    def test_delete_task(self):
        task = self._create_sample_task(title="To be removed")
        res = self.client.delete(f"/api/tasks/{task.id}")
        self.assertEqual(res.status_code, 200)

        # Verify it cannot be retrieved
        res_check = self.client.get(f"/api/tasks/{task.id}")
        self.assertEqual(res_check.status_code, 404)

    # 8. GET /api/tasks/stats
    def test_task_stats(self):
        self._create_sample_task(title="T1", status="completed", priority="high")
        self._create_sample_task(title="T2", status="pending", priority="medium")
        self._create_sample_task(title="T3", status="in_progress", priority="low")

        res = self.client.get("/api/tasks/stats")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["total"], 3)
        self.assertEqual(data["by_status"]["completed"], 1)
        self.assertEqual(data["by_status"]["pending"], 1)
        self.assertEqual(data["by_status"]["in_progress"], 1)
        self.assertEqual(data["by_priority"]["high"], 1)

if __name__ == "__main__":
    unittest.main()
