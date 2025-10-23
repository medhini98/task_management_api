# Database Schema Design Document - Task Management API (FastAPI + PostgreSQL)

## Overview

This document describes the relational database schema used for the Task Management API, which is implemented using PostgreSQL and SQLAlchemy ORM with Alembic migrations.
The goal of this design is to ensure data normalization, referential integrity, and scalability while supporting features like multi-user collaboration, tagging, and task lifecycle tracking.

⸻

## Entities & Relationships

The schema is centered around three main entities — Users, Tasks, and Tags — with two join tables (TaskAssignees and TaskTags) that model the many-to-many relationships.

### ER Diagram (Text Representation)
Users ───< TaskAssignees >─── Tasks ───< TaskTags >─── Tags
   │                              │
   │                              ├── created_by (FK → Users)
   │                              └── status, priority enums
   │
   ├── belongs_to → Departments ───< Roles
   └── reports_to (self-FK)

## Table Specifications
### 1. Users

| **Column**      | **Type**         | **Constraints**                   | **Description**                      |
|------------------|------------------|------------------------------------|--------------------------------------|
| id               | UUID             | PK                                 | Unique user ID                       |
| first_name       | VARCHAR(80)      | NOT NULL                           | User’s first name                    |
| last_name        | VARCHAR(80)      | NULL                               | Optional last name                   |
| email            | VARCHAR(255)     | UNIQUE, NOT NULL                   | Login/email ID                       |
| department_id    | UUID             | FK → departments.id                | Department association               |
| role_id          | UUID             | FK → roles.id                      | User’s role                          |
| reports_to       | UUID             | FK → users.id, NULL                | Manager’s ID (self-referencing)      |

### 2. Departments Table

| **Column** | **Type**        | **Constraints**          | **Description**         |
|-------------|----------------|---------------------------|--------------------------|
| id          | UUID           | PK                        | Department ID            |
| name        | VARCHAR(100)   | UNIQUE, NOT NULL          | Department name          |

### 3. Roles Table

| **Column**      | **Type**        | **Constraints**             | **Description**                     |
|------------------|----------------|------------------------------|-------------------------------------|
| id               | UUID           | PK                           | Role ID                             |
| department_id    | UUID           | FK → departments.id          | Linked department                   |
| name             | VARCHAR(100)   | NOT NULL                     | Role name (unique per department)   |

### 4. Tasks Table

| **Column**      | **Type**                   | **Constraints**             | **Description**                    |
|------------------|----------------------------|------------------------------|------------------------------------|
| id               | UUID                       | PK                           | Unique task ID                     |
| title            | VARCHAR(200)               | NOT NULL                     | Task title                         |
| description      | TEXT                       | NULL                         | Task description                   |
| status           | ENUM(task_status)          | DEFAULT 'todo'               | Task lifecycle stage               |
| priority         | ENUM(task_priority)        | DEFAULT 'normal'             | Task urgency                       |
| created_at       | TIMESTAMP WITH TIME ZONE   | DEFAULT NOW()                | Creation time                      |
| due_at           | TIMESTAMP WITH TIME ZONE   | NULL                         | Optional deadline                  |
| completed_at     | TIMESTAMP WITH TIME ZONE   | NULL                         | Time of completion                 |
| updated_at       | TIMESTAMP WITH TIME ZONE   | DEFAULT NOW()                | Last modified timestamp            |
| created_by       | UUID                       | FK → users.id                | Task creator                       |

#### Enums
- TaskStatus: todo, in_progress, blocked, done, cancelled
- TaskPriority: low, normal, high, urgent

#### Indexes
- (status, due_at) composite index for dashboards
- created_by FK index for fast filtering by user

### 5. Tags Table

| **Column** | **Type**      | **Constraints**    | **Description**                  |
|-------------|---------------|--------------------|----------------------------------|
| id          | UUID          | PK                 | Unique tag ID                    |
| name        | VARCHAR(64)   | UNIQUE, NOT NULL   | Tag name (e.g., backend, design) |

### 6. Task Assignees Table

| **Column**    | **Type**                 | **Constraints**                            | **Description**          |
|----------------|--------------------------|---------------------------------------------|---------------------------|
| task_id        | UUID                     | PK, FK → tasks.id, ON DELETE CASCADE       | Linked task               |
| user_id        | UUID                     | PK, FK → users.id, ON DELETE CASCADE       | Assigned user             |
| assigned_at    | TIMESTAMP WITH TIME ZONE | DEFAULT NOW()                              | When assigned             |

### 7. Task Tags Table

| **Column** | **Type** | **Constraints**                        | **Description** |
|-------------|----------|----------------------------------------|-----------------|
| task_id     | UUID     | PK, FK → tasks.id, ON DELETE CASCADE   | Linked task     |
| tag_id      | UUID     | PK, FK → tags.id, ON DELETE CASCADE    | Linked tag      |

## Normalization Summary

| **Normal Form** | **Achieved?** | **Rationale** |
|------------------|---------------|----------------|
| 1NF              | ✅            | All tables have atomic values and primary keys |
| 2NF              | ✅            | No partial dependencies (all non-key fields depend on full PK) |
| 3NF              | ✅            | No transitive dependencies (non-key fields depend only on key) |
| BCNF             | ✅            | Each determinant is a candidate key |

## Relationship Constraints

| **Relationship**                          | **Constraint Type** | **On Delete Behavior** |
|-------------------------------------------|----------------------|--------------------------|
| users.department_id → departments.id       | FK                   | RESTRICT                 |
| users.role_id → roles.id                   | FK                   | RESTRICT                 |
| users.reports_to → users.id                | Self-FK              | SET NULL                 |
| tasks.created_by → users.id                | FK                   | RESTRICT                 |
| task_assignees.task_id → tasks.id          | FK                   | CASCADE                  |
| task_assignees.user_id → users.id          | FK                   | CASCADE                  |
| task_tags.task_id → tasks.id               | FK                   | CASCADE                  |
| task_tags.tag_id → tags.id                 | FK                   | CASCADE                  |

## Sample Queries

| **Use Case**                 | **Query Type**     | **Example** |
|-------------------------------|--------------------|--------------|
| Get all open tasks            | Filter by status   | `SELECT * FROM tasks WHERE status != 'done';` |
| Find all tasks assigned to user | Join              | `SELECT t.* FROM tasks t JOIN task_assignees a ON t.id = a.task_id WHERE a.user_id = '<uuid>';` |
| List all tags for a task      | Join               | `SELECT tg.name FROM tags tg JOIN task_tags tt ON tg.id = tt.tag_id WHERE tt.task_id = '<uuid>';` |
| Get overdue tasks             | Filter by due date | `SELECT * FROM tasks WHERE due_at < NOW() AND status != 'done';` |

## Migration & Seeding Workflow
### 1. Generate Migration
```bash
alembic revision --autogenerate -m "init schema"
```

### 2. Apply Migration
```bash
alembic upgrade head
```
### 3. Seed Minimal Data
```bash
python data_db.py
```

## Schema Implementation Status

| **Aspect**               | **Status**       |
|---------------------------|------------------|
| Schema Normalization      | Up to BCNF       |
| Alembic Migration         | Working          |
| Referential Integrity     | Enforced via FK constraints |
| M2M Relationships         | Fully supported  |
| CRUD Operations           | Validated and tested |
| Test Coverage             | 93%             |