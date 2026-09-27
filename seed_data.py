"""
Database Seeder Script.
Populates initial sample tasks into the database using SQLAlchemy ORM.
"""

from datetime import datetime, timedelta
from app import create_app
from database import db
from models import Task

def seed():
    app = create_app()
    with app.app_context():
        # Check if already seeded
        count = Task.query.count()
        if count > 0:
            print(f"Database already contains {count} tasks. Skipping seeding.")
            return

        now = datetime.utcnow()
        sample_tasks = [
            Task(
                title="Configurar servidor MySQL 8.0",
                description="Instalar y verificar variables de entorno y usuarios en MySQL",
                status="completed",
                priority="high",
                category="database",
                due_date=now - timedelta(days=1)
            ),
            Task(
                title="Implementar autenticación JWT",
                description="Añadir middleware de tokens de acceso para usuarios",
                status="in_progress",
                priority="urgent",
                category="security",
                due_date=now + timedelta(days=2)
            ),
            Task(
                title="Crear documentación Swagger / OpenAPI",
                description="Generar especificación interactiva para desarrolladores frontend",
                status="pending",
                priority="medium",
                category="documentation",
                due_date=now + timedelta(days=5)
            ),
            Task(
                title="Diseñar panel de control con métricas",
                description="Visualizar tareas por estado, prioridad y tasa de completitud",
                status="pending",
                priority="low",
                category="frontend",
                due_date=now + timedelta(days=7)
            ),
            Task(
                title="Revisar tareas atrasadas (Overdue task test)",
                description="Tarea de prueba con fecha pasada sin completar para comprobar el flag is_overdue",
                status="pending",
                priority="urgent",
                category="testing",
                due_date=now - timedelta(days=3)
            )
        ]

        db.session.add_all(sample_tasks)
        db.session.commit()
        print(f"✅ Successfully seeded {len(sample_tasks)} initial tasks!")

if __name__ == "__main__":
    seed()
