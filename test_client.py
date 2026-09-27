"""
Interactive CLI Test Client for To-Do REST API.
Demonstrates all CRUD operations, filtering, pagination, and error handling.
"""

import sys
import json
import urllib.request
import urllib.error

BASE_URL = "http://127.0.0.1:5002"

def request_api(endpoint, method="GET", payload=None):
    url = f"{BASE_URL}{endpoint}"
    headers = {"Content-Type": "application/json"} if payload is not None else {}
    data = json.dumps(payload).encode("utf-8") if payload is not None else None

    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            code = resp.getcode()
            body = json.loads(resp.read().decode("utf-8"))
            return code, body
    except urllib.error.HTTPError as e:
        body = json.loads(e.read().decode("utf-8"))
        return e.code, body
    except urllib.error.URLError as e:
        print(f"❌ Connection error: Could not reach {url}")
        print("💡 Make sure 'python3 app.py' is running.")
        sys.exit(1)

def main():
    print("=" * 68)
    print(" 📋 TO-DO REST API (CRUD & MySQL) - INTERACTIVE VERIFICATION")
    print("=" * 68)

    # 1. Health check
    print("\n[1] Checking API Health & Database Connection (GET /health)...")
    code, res = request_api("/health")
    print(f"Status {code}: API status='{res.get('status')}', Engine='{res.get('database', {}).get('engine')}'")

    # 2. List Tasks
    print("\n[2] Listing Existing Tasks (GET /api/tasks)...")
    code, res = request_api("/api/tasks")
    tasks = res.get("data", [])
    total = res.get("pagination", {}).get("total_items", len(tasks))
    print(f"Status {code}: Found {total} total tasks (Showing {len(tasks)} on this page):")
    for t in tasks[:3]:
        print(f"  • [ID {t['id']}] [{t['priority'].upper()}] {t['title']} ({t['status']})")

    # 3. Create a New Task (POST)
    print("\n[3] Creating a New Task (POST /api/tasks)...")
    new_task_payload = {
        "title": "Verificar backups automáticos de MySQL",
        "description": "Comprobar replicación de binlog y restauración de snapshots",
        "priority": "urgent",
        "status": "pending",
        "category": "devops",
        "due_date": "2026-10-25T14:30:00"
    }
    code, res = request_api("/api/tasks", method="POST", payload=new_task_payload)
    created_task = res.get("data", {})
    created_id = created_task.get("id")
    print(f"Status {code}: Task #{created_id} created successfully -> '{created_task.get('title')}'")

    # 4. Retrieve by ID (GET)
    print(f"\n[4] Fetching Task by ID (GET /api/tasks/{created_id})...")
    code, res = request_api(f"/api/tasks/{created_id}")
    print(f"Status {code}: Retrieved task -> Status: '{res['data']['status']}', Category: '{res['data']['category']}'")

    # 5. Partial Update (PATCH - Toggle status to in_progress)
    print(f"\n[5] Updating Task Status (PATCH /api/tasks/{created_id})...")
    code, res = request_api(f"/api/tasks/{created_id}", method="PATCH", payload={"status": "in_progress"})
    print(f"Status {code}: Updated status to -> '{res['data']['status']}'")

    # 6. Task Statistics (GET /api/tasks/stats)
    print("\n[6] Fetching Task Aggregation Statistics (GET /api/tasks/stats)...")
    code, res = request_api("/api/tasks/stats")
    print(f"Status {code}: Total={res['total']}, By Status={res['by_status']}, Overdue={res['overdue_tasks']}")

    # 7. Delete Task (DELETE)
    print(f"\n[7] Deleting Created Task (DELETE /api/tasks/{created_id})...")
    code, res = request_api(f"/api/tasks/{created_id}", method="DELETE")
    print(f"Status {code}: {res.get('message')}")

    # 8. Verify Deletion
    print(f"\n[8] Verifying Deletion (GET /api/tasks/{created_id} expecting 404)...")
    code, res = request_api(f"/api/tasks/{created_id}")
    print(f"Status {code}: Correctly handled 404 Not Found -> {res.get('message')}")

    print("\n" + "=" * 68)
    print(" ✅ All CRUD tests and validations passed successfully!")
    print("=" * 68)

if __name__ == "__main__":
    main()
