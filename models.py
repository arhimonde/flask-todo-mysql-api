"""
Task Data Model for To-Do List Application.
"""

from datetime import datetime
from database import db

class Task(db.Model):
    __tablename__ = "tasks"

    VALID_STATUSES = ["pending", "in_progress", "completed", "cancelled"]
    VALID_PRIORITIES = ["low", "medium", "high", "urgent"]

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(150), nullable=False, index=True)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), nullable=False, default="pending", index=True)
    priority = db.Column(db.String(20), nullable=False, default="medium", index=True)
    category = db.Column(db.String(50), nullable=False, default="general", index=True)
    due_date = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def to_dict(self):
        """Serializes the task instance to a clean JSON-compatible dictionary."""
        is_overdue = False
        if self.due_date and self.status not in ["completed", "cancelled"]:
            is_overdue = self.due_date < datetime.utcnow()

        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "priority": self.priority,
            "category": self.category,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "is_overdue": is_overdue,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        return f"<Task id={self.id} title='{self.title[:20]}' status='{self.status}'>"
