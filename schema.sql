-- ========================================================
-- DDL Schema Script for MySQL 8.0 / MariaDB
-- Database: todo_db
-- ========================================================

CREATE DATABASE IF NOT EXISTS todo_db
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE todo_db;

-- --------------------------------------------------------
-- Table structure for table `tasks`
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS `tasks` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `title` VARCHAR(150) NOT NULL,
  `description` TEXT NULL,
  `status` ENUM('pending', 'in_progress', 'completed', 'cancelled') NOT NULL DEFAULT 'pending',
  `priority` ENUM('low', 'medium', 'high', 'urgent') NOT NULL DEFAULT 'medium',
  `category` VARCHAR(50) NOT NULL DEFAULT 'general',
  `due_date` DATETIME NULL,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  INDEX `idx_tasks_status` (`status`),
  INDEX `idx_tasks_priority` (`priority`),
  INDEX `idx_tasks_category` (`category`),
  INDEX `idx_tasks_due_date` (`due_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------
-- Sample Initial Data (Seed)
-- --------------------------------------------------------
INSERT INTO `tasks` (`title`, `description`, `status`, `priority`, `category`, `due_date`) VALUES
('Configurar contenedor MySQL', 'Desplegar MySQL 8.0 en Docker con docker-compose', 'completed', 'high', 'devops', '2026-09-28 10:00:00'),
('Implementar endpoint POST /api/tasks', 'Validar campos obligatorios y formato ISO de fechas', 'completed', 'urgent', 'backend', '2026-09-28 14:00:00'),
('Escribir tests unitarios', 'Crear suite de pruebas completas con cobertura de errores HTTP', 'in_progress', 'high', 'testing', '2026-09-29 18:00:00'),
('Diseñar interfaz frontend en React / Vue', 'Consumir los endpoints de la API REST', 'pending', 'medium', 'frontend', '2026-10-05 12:00:00'),
('Optimizar índices SQL para consultas por estado', 'Asegurar tiempos de respuesta inferiores a 10ms en búsquedas', 'pending', 'low', 'database', '2026-10-10 20:00:00');
