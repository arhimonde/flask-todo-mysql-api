# 📋 API REST para Gestión de Tareas (To-Do List) con Flask y MySQL

Una API RESTful completa y robusta construida con **Flask**, **SQLAlchemy** y **MySQL** (con driver `PyMySQL`). Implementa el ciclo completo de operaciones **CRUD** (Crear, Leer, Actualizar, Borrar), filtros avanzados, paginación, métricas, validación de datos y respaldo automático en SQLite para desarrollo local sin fricción.

---

## 🏗️ Arquitectura y Flujo

```
┌───────────────────────────────────────┐
│     Clientes (Frontend / cURL / Postman)│
└──────────────────┬────────────────────┘
                   │ HTTP JSON (GET, POST, PUT, PATCH, DELETE)
                   ▼
┌───────────────────────────────────────┐
│           Flask Application           │
│  ├── Blueprints: /api/tasks, /health  │
│  ├── Middleware CORS                  │
│  └── Gestor de Errores (400, 404, etc)│
└──────────────────┬────────────────────┘
                   │ SQLAlchemy ORM (2.0)
                   ▼
┌───────────────────────────────────────┐
│          Capa de Persistencia         │
│  • Primaria: MySQL 8.0 / MariaDB      │
│  • Fallback Dev: SQLite local         │
└───────────────────────────────────────┘
```

---

## ✨ Características Principales

1. **Operaciones CRUD Completas:**
   - `GET /api/tasks`: Listado con soporte para búsqueda de texto libre (`?q=`), filtros (`?status=`, `?priority=`, `?category=`), ordenación (`?sort_by=`, `?order=`) y paginación (`?page=`, `?per_page=`).
   - `GET /api/tasks/<id>`: Obtención de una tarea específica con verificación 404.
   - `POST /api/tasks`: Creación con validación estricta de esquemas, tipos y fechas ISO 8601.
   - `PUT /api/tasks/<id>`: Actualización total de los campos.
   - `PATCH /api/tasks/<id>`: Actualización parcial (por ejemplo, cambiar solo el estado o la prioridad).
   - `DELETE /api/tasks/<id>`: Eliminación persistente de la tarea.
2. **Endpoint de Métricas y Estadísticas:**
   - `GET /api/tasks/stats`: Agregados en tiempo real (total, distribución por estado, por prioridad y tareas atrasadas `overdue_tasks`).
3. **Salud y Diagnóstico:**
   - `GET /health`: Estado del servicio, motor de base de datos conectado y consumo de memoria/CPU.
4. **Respaldo Automático (Zero-Configuration Fallback):**
   - Si no hay un servidor MySQL en ejecución en `localhost:3306`, la aplicación detecta el puerto y recurre transparentemente a SQLite local (`tasks.db`), permitiendo probar y desarrollar sin dependencias externas obligatorias.
5. **Entorno Docker Completo:**
   - `docker-compose.yml` preconfigurado con MySQL 8.0, interfaz visual **Adminer** (puerto `8080`) y la API Flask.

---

## 📁 Estructura del Proyecto

```
flask_todo_mysql_api/
├── app.py                   # Factory de la app Flask, registro de rutas y manejo de errores
├── config.py                # Configuración de entornos y detección de base de datos
├── database.py              # Inicialización de SQLAlchemy y verificación de conexión
├── models.py                # Modelo SQLAlchemy de la tabla 'tasks' con serialización JSON
├── routes/
│   ├── tasks.py             # Blueprint con todas las operaciones CRUD y estadísticas
│   └── health.py            # Blueprint de healthcheck y telemetría de BD
├── schema.sql               # Script DDL de creación de base de datos y tablas para MySQL
├── seed_data.py             # Script para poblar tareas iniciales de prueba
├── test_client.py           # Cliente interactivo CLI para probar todos los endpoints
├── requirements.txt         # Dependencias Python
├── Dockerfile               # Imagen Docker para la API Flask
├── docker-compose.yml       # Orquestación de MySQL 8.0 + Adminer + Flask API
├── .env.example             # Plantilla de variables de entorno
└── tests/
    └── test_tasks.py        # Suite de 13 pruebas unitarias automatizadas
```

---

## 🚀 Instalación y Puesta en Marcha

### Opción A: Ejecución Local en Python

1. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

2. **(Opcional) Configurar credenciales de MySQL:**
   Copia el archivo `.env.example` a `.env` y ajusta los valores de tu servidor MySQL:
   ```bash
   cp .env.example .env
   ```
   > *Nota:* Si no configuras MySQL, la aplicación utilizará automáticamente SQLite local (`tasks.db`).

3. **Poblar datos de prueba:**
   ```bash
   python3 seed_data.py
   ```

4. **Iniciar el servidor:**
   ```bash
   python3 app.py
   ```
   Estará disponible en `http://0.0.0.0:5002`.

5. **Ejecutar pruebas unitarias:**
   ```bash
   python3 -m unittest discover -s tests -p "test_*.py"
   ```

6. **Ejecutar el cliente de prueba interactivo:**
   ```bash
   python3 test_client.py
   ```

---

### Opción B: Despliegue con Docker Compose (MySQL + Adminer + API)

Para levantar el entorno completo con MySQL 8.0 y Adminer con un solo comando:

```bash
docker compose up -d
```

- **API Flask:** `http://localhost:5002`
- **Adminer (Gestor Web de MySQL):** `http://localhost:8080`
  - Sistema: `MySQL`
  - Servidor: `mysql_db`
  - Usuario: `todouser`
  - Contraseña: `todopassword123`
  - Base de datos: `todo_db`

---

## 📡 Referencia de Endpoints y Ejemplos `curl`

### 1. Obtener Lista de Tareas con Filtros y Paginación
```bash
curl -X GET "http://localhost:5002/api/tasks?status=pending&priority=high&page=1&per_page=10"
```

**Respuesta:**
```json
{
  "status": "success",
  "data": [
    {
      "id": 1,
      "title": "Configurar servidor MySQL 8.0",
      "description": "Instalar y verificar variables de entorno",
      "status": "pending",
      "priority": "high",
      "category": "database",
      "due_date": "2026-10-15T18:00:00",
      "is_overdue": false,
      "created_at": "2026-09-27T12:00:00",
      "updated_at": "2026-09-27T12:00:00"
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 10,
    "total_items": 1,
    "total_pages": 1,
    "has_next": false,
    "has_prev": false
  }
}
```

---

### 2. Crear una Nueva Tarea (`POST /api/tasks`)
```bash
curl -X POST http://localhost:5002/api/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Añadir tests de integración",
    "description": "Cubrir flujos de eliminación y modificación de tareas",
    "priority": "high",
    "status": "in_progress",
    "category": "qa",
    "due_date": "2026-10-01T20:00:00"
  }'
```

**Respuesta (`201 Created`):**
```json
{
  "status": "success",
  "message": "Task created successfully.",
  "data": {
    "id": 6,
    "title": "Añadir tests de integración",
    "status": "in_progress",
    "priority": "high",
    "category": "qa"
  }
}
```

---

### 3. Modificación Parcial (`PATCH /api/tasks/<id>`)
Permite actualizar campos individuales sin enviar el objeto completo (ideal para marcar como completada):
```bash
curl -X PATCH http://localhost:5002/api/tasks/6 \
  -H "Content-Type: application/json" \
  -d '{"status": "completed"}'
```

---

### 4. Consultar Estadísticas Generales (`GET /api/tasks/stats`)
```bash
curl -X GET http://localhost:5002/api/tasks/stats
```

**Respuesta:**
```json
{
  "status": "success",
  "total": 6,
  "by_status": {
    "cancelled": 0,
    "completed": 2,
    "in_progress": 1,
    "pending": 3
  },
  "by_priority": {
    "high": 2,
    "low": 1,
    "medium": 2,
    "urgent": 1
  },
  "overdue_tasks": 1
}
```

---

### 5. Eliminar una Tarea (`DELETE /api/tasks/<id>`)
```bash
curl -X DELETE http://localhost:5002/api/tasks/6
```
