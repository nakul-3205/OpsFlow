# OpsFlow - Complete Development Plan & API Contract

## Executive Summary

OpsFlow is an event-driven operations backend that autonomously enforces SLAs, manages task lifecycles, and provides operational intelligence through metrics and audit trails. This document outlines the complete development plan following microservices architecture principles.

---

## 1. Architecture Overview

### 1.1 Microservices-Style Design

While deployed as a modular monolith initially, the system is architected with clear service boundaries for future extraction:

```
┌─────────────────────────────────────────────────────────────┐
│                     API Gateway (Nginx)                      │
│                    (Routing, SSL, Rate Limiting)             │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                   FastAPI Application Layer                  │
└─────────────────────────────────────────────────────────────┘
                              ↓
    ┌──────────────┬──────────────┬──────────────┬──────────────┐
    │              │              │              │              │
┌───▼────┐  ┌──────▼─────┐  ┌────▼─────┐  ┌─────▼──────┐  ┌───▼────┐
│  Auth  │  │   Task     │  │   SLA    │  │  Reporting │  │ Notif  │
│Service │  │  Service   │  │ Service  │  │  Service   │  │Service │
└───┬────┘  └──────┬─────┘  └────┬─────┘  └─────┬──────┘  └───┬────┘
    │              │              │              │              │
    └──────────────┴──────────────┴──────────────┴──────────────┘
                              ↓
         ┌────────────────────────────────────────┐
         │         Data & Infrastructure          │
         │  ┌──────────────┐  ┌─────────────┐   │
         │  │  PostgreSQL  │  │    Redis    │   │
         │  │  (Primary)   │  │ (Cache/MQ)  │   │
         │  └──────────────┘  └─────────────┘   │
         └────────────────────────────────────────┘
                              ↓
         ┌────────────────────────────────────────┐
         │        Background Processing           │
         │  ┌──────────────┐  ┌─────────────┐   │
         │  │    Celery    │  │  Celery     │   │
         │  │   Workers    │  │   Beat      │   │
         │  └──────────────┘  └─────────────┘   │
         └────────────────────────────────────────┘
                              ↓
         ┌────────────────────────────────────────┐
         │      Observability Stack               │
         │  ┌──────────────┐  ┌─────────────┐   │
         │  │  Prometheus  │  │   Grafana   │   │
         │  │  (Metrics)   │  │(Dashboard)  │   │
         │  └──────────────┘  └─────────────┘   │
         └────────────────────────────────────────┘
```

### 1.2 Service Boundaries

Each "service" is a Python module with clear interfaces:

- **Auth Service**: JWT issuance, validation, refresh
- **Task Service**: Task CRUD, state transitions, assignments
- **SLA Service**: Timer scheduling, breach detection, escalations
- **Notification Service**: Multi-channel notifications (email, webhook, SMS mock)
- **Reporting Service**: Analytics, dashboards, SLA metrics
- **Audit Service**: Event logging, compliance trails

---

## 2. Technology Stack (Detailed)

### 2.1 Core Application

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| Language | Python | 3.11+ | Primary language |
| API Framework | FastAPI | 0.109+ | REST API with OpenAPI |
| ASGI Server | Uvicorn | 0.27+ | Production server |
| Validation | Pydantic | 2.5+ | Request/response validation |
| Auth | python-jose[cryptography] | 3.3+ | JWT handling |
| Password | passlib[bcrypt] | 1.7+ | Password hashing |

### 2.2 Database Layer

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| Database | PostgreSQL | 15+ | Primary data store |
| ORM | SQLAlchemy | 2.0+ | Database abstraction |
| Migrations | Alembic | 1.13+ | Schema versioning |
| Connection Pool | psycopg2-binary | 2.9+ | Postgres driver |
| Async Driver | asyncpg | 0.29+ | Async database ops |

### 2.3 Caching & Queue

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| Cache | Redis | 7.2+ | Fast data access |
| Queue Broker | Redis | 7.2+ | Message queue |
| Client | redis-py | 5.0+ | Python Redis client |
| Rate Limiting | redis | 7.2+ | API throttling |

### 2.4 Background Processing

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| Task Queue | Celery | 5.3+ | Async task execution |
| Scheduler | Celery Beat | 5.3+ | Periodic tasks |
| Result Backend | Redis | 7.2+ | Task result storage |
| Serializer | JSON | - | Message serialization |

### 2.5 Observability

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| Logging | structlog | 24.1+ | Structured logging |
| Metrics | prometheus-client | 0.19+ | Metrics collection |
| Dashboard | Grafana | 10.0+ | Visualization |
| Tracing (Optional) | OpenTelemetry | 1.21+ | Distributed tracing |

### 2.6 Testing & Quality

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| Testing | pytest | 7.4+ | Test framework |
| Async Testing | pytest-asyncio | 0.23+ | Async test support |
| Coverage | pytest-cov | 4.1+ | Code coverage |
| Mocking | pytest-mock | 3.12+ | Mock objects |
| Factories | factory-boy | 3.3+ | Test data generation |
| HTTP Testing | httpx | 0.26+ | API client testing |
| Load Testing | k6 | 0.49+ | Performance testing |

### 2.7 Security & Compliance

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| Security Scan | Bandit | 1.7+ | Python security linter |
| Dependency Check | Safety | 3.0+ | Vulnerability scanning |
| Secrets | python-dotenv | 1.0+ | Environment variables |
| OWASP Testing | OWASP ZAP | 2.14+ | Security testing |

### 2.8 DevOps & Deployment

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| Containerization | Docker | 24.0+ | Application packaging |
| Orchestration | Docker Compose | 2.23+ | Local development |
| CI/CD | GitHub Actions | - | Automation pipeline |
| Reverse Proxy | Nginx | 1.25+ | API Gateway |
| Process Manager | Supervisor | 4.2+ | Service management |

---

## 3. Database Schema

### 3.1 Core Tables

```sql
-- Users Table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    role VARCHAR(50) NOT NULL CHECK (role IN ('admin', 'developer', 'manager')),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);

-- Tasks/Incidents Table
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(500) NOT NULL,
    description TEXT,
    task_type VARCHAR(50) NOT NULL CHECK (task_type IN ('TASK', 'INCIDENT')),
    priority VARCHAR(50) NOT NULL CHECK (priority IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')),
    status VARCHAR(50) NOT NULL CHECK (status IN ('CREATED', 'ASSIGNED', 'IN_PROGRESS', 'BLOCKED', 'COMPLETED', 'CANCELLED')),

    -- Assignment
    created_by UUID NOT NULL REFERENCES users(id),
    assigned_to UUID REFERENCES users(id),

    -- SLA Configuration
    start_sla_minutes INTEGER NOT NULL,
    resolve_sla_minutes INTEGER NOT NULL,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    assigned_at TIMESTAMP WITH TIME ZONE,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- Metadata
    tags TEXT[],
    metadata JSONB DEFAULT '{}'
);

CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_assigned_to ON tasks(assigned_to);
CREATE INDEX idx_tasks_priority ON tasks(priority);
CREATE INDEX idx_tasks_created_at ON tasks(created_at DESC);
CREATE INDEX idx_tasks_type ON tasks(task_type);

-- SLA Events Table
CREATE TABLE sla_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    event_type VARCHAR(50) NOT NULL CHECK (event_type IN ('START_WARNING', 'START_BREACH', 'RESOLVE_WARNING', 'RESOLVE_BREACH', 'ESCALATION')),
    severity VARCHAR(50) NOT NULL CHECK (severity IN ('INFO', 'WARNING', 'CRITICAL')),

    -- SLA Details
    sla_type VARCHAR(50) NOT NULL CHECK (sla_type IN ('START', 'RESOLVE')),
    expected_deadline TIMESTAMP WITH TIME ZONE NOT NULL,
    actual_time TIMESTAMP WITH TIME ZONE,
    delay_minutes INTEGER,

    -- Notification
    notification_sent BOOLEAN DEFAULT false,
    notification_sent_at TIMESTAMP WITH TIME ZONE,

    -- Escalation
    escalated_to UUID REFERENCES users(id),
    escalation_level INTEGER DEFAULT 0,

    triggered_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    metadata JSONB DEFAULT '{}'
);

CREATE INDEX idx_sla_events_task_id ON sla_events(task_id);
CREATE INDEX idx_sla_events_type ON sla_events(event_type);
CREATE INDEX idx_sla_events_triggered_at ON sla_events(triggered_at DESC);

-- Audit Logs Table
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_type VARCHAR(100) NOT NULL,
    entity_id UUID NOT NULL,
    action VARCHAR(100) NOT NULL,

    -- Actor Information
    actor_type VARCHAR(50) NOT NULL CHECK (actor_type IN ('user', 'system', 'api')),
    actor_id UUID REFERENCES users(id),

    -- Change Details
    previous_state JSONB,
    new_state JSONB,
    changes JSONB,

    -- Context
    ip_address INET,
    user_agent TEXT,

    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    metadata JSONB DEFAULT '{}'
);

CREATE INDEX idx_audit_logs_entity ON audit_logs(entity_type, entity_id);
CREATE INDEX idx_audit_logs_actor ON audit_logs(actor_id);
CREATE INDEX idx_audit_logs_timestamp ON audit_logs(timestamp DESC);
CREATE INDEX idx_audit_logs_action ON audit_logs(action);

-- Notifications Table
CREATE TABLE notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id UUID REFERENCES tasks(id) ON DELETE CASCADE,
    sla_event_id UUID REFERENCES sla_events(id) ON DELETE SET NULL,

    -- Notification Details
    notification_type VARCHAR(50) NOT NULL CHECK (notification_type IN ('EMAIL', 'WEBHOOK', 'SMS', 'SLACK')),
    recipient_id UUID REFERENCES users(id),
    recipient_address VARCHAR(500) NOT NULL,

    -- Content
    subject VARCHAR(500),
    body TEXT NOT NULL,
    template_name VARCHAR(100),

    -- Status
    status VARCHAR(50) NOT NULL CHECK (status IN ('PENDING', 'SENT', 'FAILED', 'RETRY')),
    attempts INTEGER DEFAULT 0,
    max_attempts INTEGER DEFAULT 3,

    -- Timestamps
    scheduled_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    sent_at TIMESTAMP WITH TIME ZONE,
    failed_at TIMESTAMP WITH TIME ZONE,

    -- Error Tracking
    error_message TEXT,

    metadata JSONB DEFAULT '{}'
);

CREATE INDEX idx_notifications_task_id ON notifications(task_id);
CREATE INDEX idx_notifications_status ON notifications(status);
CREATE INDEX idx_notifications_recipient ON notifications(recipient_id);
CREATE INDEX idx_notifications_scheduled_at ON notifications(scheduled_at);

-- SLA Configurations Table (for flexible SLA rules)
CREATE TABLE sla_configurations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    task_type VARCHAR(50) NOT NULL,
    priority VARCHAR(50) NOT NULL,

    -- SLA Timings
    start_sla_minutes INTEGER NOT NULL,
    resolve_sla_minutes INTEGER NOT NULL,

    -- Warning Thresholds (% of SLA)
    start_warning_threshold DECIMAL(5,2) DEFAULT 75.0,
    resolve_warning_threshold DECIMAL(5,2) DEFAULT 75.0,

    -- Escalation Rules
    escalation_chain UUID[] DEFAULT '{}',

    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE UNIQUE INDEX idx_sla_config_unique ON sla_configurations(task_type, priority) WHERE is_active = true;
```

### 3.2 Materialized Views for Reporting

```sql
-- SLA Performance Summary (Refreshed periodically)
CREATE MATERIALIZED VIEW sla_performance_summary AS
SELECT
    DATE_TRUNC('day', t.created_at) as date,
    t.task_type,
    t.priority,
    COUNT(*) as total_tasks,
    COUNT(CASE WHEN t.status = 'COMPLETED' THEN 1 END) as completed_tasks,
    COUNT(CASE WHEN se.event_type LIKE '%BREACH' THEN 1 END) as breached_tasks,
    AVG(EXTRACT(EPOCH FROM (t.started_at - t.created_at)) / 60) as avg_start_time_minutes,
    AVG(EXTRACT(EPOCH FROM (t.completed_at - t.created_at)) / 60) as avg_completion_time_minutes
FROM tasks t
LEFT JOIN sla_events se ON t.id = se.task_id
GROUP BY DATE_TRUNC('day', t.created_at), t.task_type, t.priority;

CREATE UNIQUE INDEX idx_sla_perf_summary ON sla_performance_summary(date, task_type, priority);

-- Active Task Dashboard
CREATE MATERIALIZED VIEW active_tasks_dashboard AS
SELECT
    t.id,
    t.title,
    t.task_type,
    t.priority,
    t.status,
    t.assigned_to,
    u.full_name as assignee_name,
    t.created_at,
    t.start_sla_minutes,
    t.resolve_sla_minutes,
    CASE
        WHEN t.status IN ('CREATED', 'ASSIGNED') THEN
            t.created_at + (t.start_sla_minutes || ' minutes')::INTERVAL
        ELSE NULL
    END as start_deadline,
    CASE
        WHEN t.status NOT IN ('COMPLETED', 'CANCELLED') THEN
            t.created_at + (t.resolve_sla_minutes || ' minutes')::INTERVAL
        ELSE NULL
    END as resolve_deadline,
    EXISTS(SELECT 1 FROM sla_events se WHERE se.task_id = t.id AND se.event_type LIKE '%BREACH') as has_breach
FROM tasks t
LEFT JOIN users u ON t.assigned_to = u.id
WHERE t.status NOT IN ('COMPLETED', 'CANCELLED');

CREATE UNIQUE INDEX idx_active_tasks_id ON active_tasks_dashboard(id);
```

---

## 4. Complete API Contract

### 4.1 API Versioning & Base URL

```
Base URL: https://api.opsflow.io/api/v1
```

All endpoints are prefixed with `/api/v1` for versioning.

### 4.2 Authentication Endpoints

#### POST /auth/register
Register a new user (Admin only)

**Request:**
```json
{
  "email": "john.doe@example.com",
  "username": "johndoe",
  "password": "SecureP@ss123",
  "full_name": "John Doe",
  "role": "developer"
}
```

**Response: 201 Created**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "john.doe@example.com",
  "username": "johndoe",
  "full_name": "John Doe",
  "role": "developer",
  "is_active": true,
  "created_at": "2026-01-27T10:30:00Z"
}
```

#### POST /auth/login
Authenticate and receive JWT tokens

**Request:**
```json
{
  "username": "johndoe",
  "password": "SecureP@ss123"
}
```

**Response: 200 OK**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "username": "johndoe",
    "email": "john.doe@example.com",
    "role": "developer"
  }
}
```

#### POST /auth/refresh
Refresh access token

**Request:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response: 200 OK**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

#### POST /auth/logout
Invalidate refresh token

**Request Headers:**
```
Authorization: Bearer <access_token>
```

**Response: 204 No Content**

### 4.3 Task Management Endpoints

#### POST /tasks
Create a new task or incident (Admin/Manager only)

**Request:**
```json
{
  "title": "Database connection pool exhaustion",
  "description": "Production DB hitting max connections during peak hours",
  "task_type": "INCIDENT",
  "priority": "CRITICAL",
  "assigned_to": "550e8400-e29b-41d4-a716-446655440001",
  "start_sla_minutes": 15,
  "resolve_sla_minutes": 120,
  "tags": ["database", "production", "performance"],
  "metadata": {
    "affected_service": "api-gateway",
    "customer_impact": "high"
  }
}
```

**Response: 201 Created**
```json
{
  "id": "660e8400-e29b-41d4-a716-446655440000",
  "title": "Database connection pool exhaustion",
  "description": "Production DB hitting max connections during peak hours",
  "task_type": "INCIDENT",
  "priority": "CRITICAL",
  "status": "ASSIGNED",
  "created_by": "550e8400-e29b-41d4-a716-446655440000",
  "assigned_to": "550e8400-e29b-41d4-a716-446655440001",
  "start_sla_minutes": 15,
  "resolve_sla_minutes": 120,
  "created_at": "2026-01-27T10:30:00Z",
  "assigned_at": "2026-01-27T10:30:00Z",
  "started_at": null,
  "completed_at": null,
  "tags": ["database", "production", "performance"],
  "metadata": {
    "affected_service": "api-gateway",
    "customer_impact": "high"
  },
  "sla_status": {
    "start_deadline": "2026-01-27T10:45:00Z",
    "resolve_deadline": "2026-01-27T12:30:00Z",
    "time_remaining": {
      "start": "15 minutes",
      "resolve": "2 hours"
    }
  }
}
```

#### GET /tasks
List tasks with filtering and pagination

**Query Parameters:**
- `status`: Filter by status (CREATED, ASSIGNED, IN_PROGRESS, etc.)
- `priority`: Filter by priority (LOW, MEDIUM, HIGH, CRITICAL)
- `task_type`: Filter by type (TASK, INCIDENT)
- `assigned_to`: Filter by assignee user ID
- `has_breach`: Boolean, filter tasks with SLA breaches
- `page`: Page number (default: 1)
- `page_size`: Items per page (default: 20, max: 100)
- `sort`: Sort field (created_at, priority, deadline)
- `order`: Sort order (asc, desc)

**Example Request:**
```
GET /tasks?status=IN_PROGRESS&priority=CRITICAL&page=1&page_size=20&sort=created_at&order=desc
```

**Response: 200 OK**
```json
{
  "items": [
    {
      "id": "660e8400-e29b-41d4-a716-446655440000",
      "title": "Database connection pool exhaustion",
      "task_type": "INCIDENT",
      "priority": "CRITICAL",
      "status": "IN_PROGRESS",
      "assigned_to": {
        "id": "550e8400-e29b-41d4-a716-446655440001",
        "username": "jane.smith",
        "full_name": "Jane Smith"
      },
      "created_at": "2026-01-27T10:30:00Z",
      "started_at": "2026-01-27T10:35:00Z",
      "sla_status": {
        "start_met": true,
        "resolve_deadline": "2026-01-27T12:30:00Z",
        "time_remaining": "1 hour 55 minutes",
        "at_risk": false
      }
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total_items": 45,
    "total_pages": 3,
    "has_next": true,
    "has_previous": false
  }
}
```

#### GET /tasks/{task_id}
Get task details

**Response: 200 OK**
```json
{
  "id": "660e8400-e29b-41d4-a716-446655440000",
  "title": "Database connection pool exhaustion",
  "description": "Production DB hitting max connections during peak hours",
  "task_type": "INCIDENT",
  "priority": "CRITICAL",
  "status": "IN_PROGRESS",
  "created_by": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "username": "admin",
    "full_name": "System Admin"
  },
  "assigned_to": {
    "id": "550e8400-e29b-41d4-a716-446655440001",
    "username": "jane.smith",
    "full_name": "Jane Smith"
  },
  "start_sla_minutes": 15,
  "resolve_sla_minutes": 120,
  "created_at": "2026-01-27T10:30:00Z",
  "assigned_at": "2026-01-27T10:30:00Z",
  "started_at": "2026-01-27T10:35:00Z",
  "completed_at": null,
  "updated_at": "2026-01-27T10:35:00Z",
  "tags": ["database", "production", "performance"],
  "metadata": {
    "affected_service": "api-gateway",
    "customer_impact": "high"
  },
  "sla_status": {
    "start_deadline": "2026-01-27T10:45:00Z",
    "start_met": true,
    "start_time_taken": "5 minutes",
    "resolve_deadline": "2026-01-27T12:30:00Z",
    "time_remaining": "1 hour 55 minutes",
    "at_risk": false,
    "breach_count": 0
  },
  "sla_events": [
    {
      "id": "770e8400-e29b-41d4-a716-446655440000",
      "event_type": "START_WARNING",
      "severity": "WARNING",
      "triggered_at": "2026-01-27T10:41:15Z",
      "notification_sent": true
    }
  ],
  "audit_trail": [
    {
      "action": "TASK_CREATED",
      "actor": "admin",
      "timestamp": "2026-01-27T10:30:00Z"
    },
    {
      "action": "TASK_STARTED",
      "actor": "jane.smith",
      "timestamp": "2026-01-27T10:35:00Z"
    }
  ]
}
```

#### PATCH /tasks/{task_id}/start
Mark task as started (Developer/Assignee only)

**Response: 200 OK**
```json
{
  "id": "660e8400-e29b-41d4-a716-446655440000",
  "status": "IN_PROGRESS",
  "started_at": "2026-01-27T10:35:00Z",
  "sla_status": {
    "start_met": true,
    "start_time_taken": "5 minutes"
  }
}
```

#### PATCH /tasks/{task_id}/complete
Mark task as completed (Developer/Assignee only)

**Request:**
```json
{
  "resolution_notes": "Increased connection pool size from 20 to 50. Monitoring for 24h."
}
```

**Response: 200 OK**
```json
{
  "id": "660e8400-e29b-41d4-a716-446655440000",
  "status": "COMPLETED",
  "completed_at": "2026-01-27T11:45:00Z",
  "sla_status": {
    "start_met": true,
    "resolve_met": true,
    "total_time": "1 hour 15 minutes"
  }
}
```

#### PATCH /tasks/{task_id}/assign
Reassign task (Admin/Manager only)

**Request:**
```json
{
  "assigned_to": "550e8400-e29b-41d4-a716-446655440002"
}
```

**Response: 200 OK**
```json
{
  "id": "660e8400-e29b-41d4-a716-446655440000",
  "assigned_to": {
    "id": "550e8400-e29b-41d4-a716-446655440002",
    "username": "bob.jones",
    "full_name": "Bob Jones"
  },
  "assigned_at": "2026-01-27T11:00:00Z"
}
```

#### PATCH /tasks/{task_id}
Update task details (Admin/Manager only)

**Request:**
```json
{
  "priority": "HIGH",
  "description": "Updated description with new findings",
  "tags": ["database", "production", "performance", "resolved"]
}
```

**Response: 200 OK**
```json
{
  "id": "660e8400-e29b-41d4-a716-446655440000",
  "priority": "HIGH",
  "description": "Updated description with new findings",
  "tags": ["database", "production", "performance", "resolved"],
  "updated_at": "2026-01-27T11:50:00Z"
}
```

#### DELETE /tasks/{task_id}
Cancel a task (Admin only)

**Response: 204 No Content**

### 4.4 SLA & Events Endpoints

#### GET /tasks/{task_id}/sla-events
Get SLA events for a task

**Response: 200 OK**
```json
{
  "task_id": "660e8400-e29b-41d4-a716-446655440000",
  "events": [
    {
      "id": "770e8400-e29b-41d4-a716-446655440001",
      "event_type": "START_WARNING",
      "severity": "WARNING",
      "sla_type": "START",
      "expected_deadline": "2026-01-27T10:45:00Z",
      "triggered_at": "2026-01-27T10:41:15Z",
      "notification_sent": true,
      "notification_sent_at": "2026-01-27T10:41:16Z"
    },
    {
      "id": "770e8400-e29b-41d4-a716-446655440002",
      "event_type": "RESOLVE_WARNING",
      "severity": "WARNING",
      "sla_type": "RESOLVE",
      "expected_deadline": "2026-01-27T12:30:00Z",
      "triggered_at": "2026-01-27T11:52:30Z",
      "notification_sent": true,
      "notification_sent_at": "2026-01-27T11:52:31Z"
    }
  ],
  "summary": {
    "total_events": 2,
    "warnings": 2,
    "breaches": 0,
    "escalations": 0
  }
}
```

#### GET /sla-events
List all SLA events with filtering

**Query Parameters:**
- `event_type`: Filter by event type
- `severity`: Filter by severity
- `start_date`: Filter events after date
- `end_date`: Filter events before date
- `page`, `page_size`: Pagination

**Response: 200 OK**
```json
{
  "items": [
    {
      "id": "770e8400-e29b-41d4-a716-446655440001",
      "task": {
        "id": "660e8400-e29b-41d4-a716-446655440000",
        "title": "Database connection pool exhaustion",
        "priority": "CRITICAL"
      },
      "event_type": "RESOLVE_BREACH",
      "severity": "CRITICAL",
      "triggered_at": "2026-01-27T12:31:00Z",
      "delay_minutes": 1
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total_items": 156,
    "total_pages": 8
  }
}
```

### 4.5 Reporting & Analytics Endpoints

#### GET /reports/sla-summary
Get SLA performance summary

**Query Parameters:**
- `start_date`: Start date (default: 30 days ago)
- `end_date`: End date (default: today)
- `task_type`: Filter by task type
- `priority`: Filter by priority
- `group_by`: Grouping (day, week, month)

**Response: 200 OK**
```json
{
  "period": {
    "start": "2026-01-01T00:00:00Z",
    "end": "2026-01-27T23:59:59Z"
  },
  "overall_metrics": {
    "total_tasks": 1250,
    "completed_tasks": 1180,
    "in_progress_tasks": 45,
    "cancelled_tasks": 25,
    "completion_rate": 94.4,
    "avg_completion_time_hours": 4.2,
    "sla_breach_rate": 8.5,
    "total_breaches": 106
  },
  "by_priority": [
    {
      "priority": "CRITICAL",
      "total": 85,
      "completed": 82,
      "breaches": 2,
      "breach_rate": 2.4,
      "avg_completion_time_hours": 1.8
    },
    {
      "priority": "HIGH",
      "total": 320,
      "completed": 305,
      "breaches": 18,
      "breach_rate": 5.6,
      "avg_completion_time_hours": 3.5
    }
  ],
  "by_type": [
    {
      "task_type": "INCIDENT",
      "total": 180,
      "completed": 175,
      "breaches": 12,
      "breach_rate": 6.7,
      "avg_completion_time_hours": 2.1
    },
    {
      "task_type": "TASK",
      "total": 1070,
      "completed": 1005,
      "breaches": 94,
      "breach_rate": 8.8,
      "avg_completion_time_hours": 4.8
    }
  ],
  "time_series": [
    {
      "date": "2026-01-20",
      "total": 42,
      "completed": 40,
      "breaches": 3
    },
    {
      "date": "2026-01-21",
      "total": 51,
      "completed": 48,
      "breaches": 5
    }
  ]
}
```

#### GET /reports/team-performance
Get team performance metrics

**Response: 200 OK**
```json
{
  "team_metrics": [
    {
      "user": {
        "id": "550e8400-e29b-41d4-a716-446655440001",
        "username": "jane.smith",
        "full_name": "Jane Smith"
      },
      "assigned_tasks": 85,
      "completed_tasks": 78,
      "in_progress_tasks": 5,
      "avg_completion_time_hours": 3.2,
      "sla_breaches": 4,
      "breach_rate": 4.7,
      "workload_score": 72
    }
  ]
}
```

#### GET /reports/incidents
Get incident-specific analytics

**Response: 200 OK**
```json
{
  "incident_metrics": {
    "total_incidents": 180,
    "open_incidents": 12,
    "mttr_hours": 2.3,
    "mttr_trend": "improving",
    "by_severity": {
      "CRITICAL": 15,
      "HIGH": 68,
      "MEDIUM": 82,
      "LOW": 15
    },
    "top_categories": [
      {
        "category": "database",
        "count": 45,
        "avg_resolution_hours": 1.8
      }
    ]
  }
}
```

#### GET /reports/dashboard
Get real-time dashboard data

**Response: 200 OK**
```json
{
  "realtime_stats": {
    "active_incidents": 12,
    "critical_incidents": 2,
    "tasks_at_risk": 8,
    "pending_escalations": 3,
    "team_utilization": 78
  },
  "recent_breaches": [
    {
      "task_id": "660e8400-e29b-41d4-a716-446655440005",
      "title": "API timeout errors",
      "breach_type": "RESOLVE_BREACH",
      "delay_minutes": 15,
      "triggered_at": "2026-01-27T11:45:00Z"
    }
  ],
  "upcoming_deadlines": [
    {
      "task_id": "660e8400-e29b-41d4-a716-446655440006",
      "title": "Deploy security patch",
      "deadline": "2026-01-27T14:30:00Z",
      "time_remaining": "2 hours 15 minutes",
      "at_risk": true
    }
  ]
}
```

### 4.6 Audit & Compliance Endpoints

#### GET /audit-logs
Retrieve audit logs

**Query Parameters:**
- `entity_type`: Filter by entity (task, user, etc.)
- `entity_id`: Filter by specific entity ID
- `action`: Filter by action type
- `actor_id`: Filter by actor
- `start_date`, `end_date`: Date range
- `page`, `page_size`: Pagination

**Response: 200 OK**
```json
{
  "items": [
    {
      "id": "880e8400-e29b-41d4-a716-446655440000",
      "entity_type": "task",
      "entity_id": "660e8400-e29b-41d4-a716-446655440000",
      "action": "TASK_STATUS_CHANGED",
      "actor_type": "user",
      "actor": {
        "id": "550e8400-e29b-41d4-a716-446655440001",
        "username": "jane.smith"
      },
      "changes": {
        "status": {
          "from": "ASSIGNED",
          "to": "IN_PROGRESS"
        }
      },
      "timestamp": "2026-01-27T10:35:00Z",
      "ip_address": "192.168.1.100",
      "user_agent": "Mozilla/5.0..."
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 50,
    "total_items": 15420
  }
}
```

#### GET /audit-logs/export
Export audit logs (CSV/JSON)

**Query Parameters:**
- All filters from GET /audit-logs
- `format`: Export format (csv, json)

**Response: 200 OK**
Returns file download with appropriate Content-Type.

### 4.7 Notification Management Endpoints

#### GET /notifications
List notifications

**Query Parameters:**
- `task_id`: Filter by task
- `status`: Filter by status (PENDING, SENT, FAILED)
- `notification_type`: Filter by type
- `page`, `page_size`: Pagination

**Response: 200 OK**
```json
{
  "items": [
    {
      "id": "990e8400-e29b-41d4-a716-446655440000",
      "task_id": "660e8400-e29b-41d4-a716-446655440000",
      "notification_type": "EMAIL",
      "recipient": {
        "id": "550e8400-e29b-41d4-a716-446655440001",
        "email": "jane.smith@example.com"
      },
      "subject": "SLA Warning: Database connection pool exhaustion",
      "status": "SENT",
      "attempts": 1,
      "scheduled_at": "2026-01-27T10:41:15Z",
      "sent_at": "2026-01-27T10:41:16Z"
    }
  ]
}
```

#### POST /notifications/{notification_id}/retry
Retry failed notification (Admin only)

**Response: 200 OK**
```json
{
  "id": "990e8400-e29b-41d4-a716-446655440000",
  "status": "PENDING",
  "attempts": 2
}
```

### 4.8 System Health & Metrics Endpoints

#### GET /health
System health check

**Response: 200 OK**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2026-01-27T12:00:00Z",
  "services": {
    "database": {
      "status": "healthy",
      "latency_ms": 5
    },
    "redis": {
      "status": "healthy",
      "latency_ms": 2
    },
    "celery_workers": {
      "status": "healthy",
      "active_workers": 4,
      "pending_tasks": 12
    }
  }
}
```

#### GET /metrics
Prometheus metrics endpoint

**Response: 200 OK** (Prometheus format)
```
# HELP opsflow_tasks_total Total number of tasks
# TYPE opsflow_tasks_total counter
opsflow_tasks_total{status="completed"} 1180
opsflow_tasks_total{status="in_progress"} 45

# HELP opsflow_sla_breaches_total Total SLA breaches
# TYPE opsflow_sla_breaches_total counter
opsflow_sla_breaches_total{type="start"} 45
opsflow_sla_breaches_total{type="resolve"} 61
```

### 4.9 Error Response Format

All error responses follow this standard format:

**400 Bad Request**
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": [
      {
        "field": "priority",
        "message": "Must be one of: LOW, MEDIUM, HIGH, CRITICAL"
      }
    ],
    "timestamp": "2026-01-27T12:00:00Z",
    "request_id": "req_abc123"
  }
}
```

**401 Unauthorized**
```json
{
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Invalid or expired token",
    "timestamp": "2026-01-27T12:00:00Z",
    "request_id": "req_abc123"
  }
}
```

**403 Forbidden**
```json
{
  "error": {
    "code": "FORBIDDEN",
    "message": "Insufficient permissions to perform this action",
    "required_role": "admin",
    "timestamp": "2026-01-27T12:00:00Z",
    "request_id": "req_abc123"
  }
}
```

**404 Not Found**
```json
{
  "error": {
    "code": "NOT_FOUND",
    "message": "Task not found",
    "entity_type": "task",
    "entity_id": "660e8400-e29b-41d4-a716-446655440099",
    "timestamp": "2026-01-27T12:00:00Z",
    "request_id": "req_abc123"
  }
}
```

**500 Internal Server Error**
```json
{
  "error": {
    "code": "INTERNAL_ERROR",
    "message": "An unexpected error occurred",
    "timestamp": "2026-01-27T12:00:00Z",
    "request_id": "req_abc123"
  }
}
```

---

## 5. Development Phases & Timeline

### Phase 1: Foundation (Weeks 1-2)

**Week 1: Core Infrastructure**
- [ ] Project setup and repository structure
- [ ] Docker Compose environment (PostgreSQL, Redis)
- [ ] FastAPI application skeleton
- [ ] Database schema creation with Alembic
- [ ] Basic CI/CD pipeline (linting, formatting)
- [ ] Development environment documentation

**Week 2: Authentication & User Management**
- [ ] JWT authentication implementation
- [ ] User registration and login endpoints
- [ ] Password hashing with bcrypt
- [ ] Role-based access control (RBAC)
- [ ] Token refresh mechanism
- [ ] Unit tests for auth service

**Deliverables:**
- Running local development environment
- Working authentication system
- Initial test suite with >80% coverage

### Phase 2: Core Task Management (Weeks 3-4)

**Week 3: Task CRUD Operations**
- [ ] Task creation endpoint
- [ ] Task retrieval (single & list with pagination)
- [ ] Task update and deletion
- [ ] Task assignment logic
- [ ] Status transition validations
- [ ] Input validation with Pydantic

**Week 4: Task Lifecycle & State Management**
- [ ] Start task endpoint
- [ ] Complete task endpoint
- [ ] Task reassignment
- [ ] Audit log creation for all actions
- [ ] Integration tests for task flows
- [ ] API documentation with OpenAPI

**Deliverables:**
- Complete task management API
- Comprehensive test coverage
- API documentation

### Phase 3: SLA Engine (Weeks 5-6)

**Week 5: Celery Setup & Basic SLA Tracking**
- [ ] Celery worker configuration
- [ ] Celery Beat scheduler setup
- [ ] SLA timer scheduling on task creation
- [ ] SLA deadline calculation logic
- [ ] Basic SLA check workers
- [ ] Redis queue monitoring

**Week 6: SLA Events & Escalations**
- [ ] SLA warning detection
- [ ] SLA breach detection
- [ ] Escalation logic implementation
- [ ] SLA event logging
- [ ] SLA status endpoint
- [ ] Worker failure handling and retries

**Deliverables:**
- Autonomous SLA monitoring system
- Escalation workflows
- Worker monitoring dashboard

### Phase 4: Notification System (Weeks 7-8)

**Week 7: Notification Infrastructure**
- [ ] Notification service architecture
- [ ] Email notification templates
- [ ] Webhook notification support
- [ ] Mock SMS provider integration
- [ ] Notification queue management
- [ ] Retry logic for failed notifications

**Week 8: Notification Reliability**
- [ ] Dead letter queue for failures
- [ ] Notification status tracking
- [ ] Manual retry endpoint
- [ ] Notification history endpoint
- [ ] Template management
- [ ] Integration tests for notification flows

**Deliverables:**
- Multi-channel notification system
- Reliable delivery with retries
- Notification audit trail

### Phase 5: Reporting & Analytics (Weeks 9-10)

**Week 9: Core Reporting**
- [ ] SLA summary report endpoint
- [ ] Team performance report
- [ ] Incident analytics
- [ ] Materialized view creation
- [ ] Report caching strategy
- [ ] Export functionality (CSV/JSON)

**Week 10: Dashboard & Real-time Metrics**
- [ ] Real-time dashboard endpoint
- [ ] Prometheus metrics integration
- [ ] Grafana dashboard setup
- [ ] Performance optimization
- [ ] Query optimization
- [ ] Caching implementation

**Deliverables:**
- Comprehensive reporting system
- Metrics and monitoring
- Grafana dashboards

### Phase 6: Hardening & Production Prep (Weeks 11-12)

**Week 11: Security & Performance**
- [ ] Security audit (Bandit, OWASP ZAP)
- [ ] Rate limiting implementation
- [ ] Input sanitization review
- [ ] SQL injection prevention
- [ ] XSS protection
- [ ] Load testing with k6
- [ ] Performance profiling
- [ ] Database query optimization

**Week 12: Production Deployment**
- [ ] Nginx reverse proxy setup
- [ ] SSL/TLS configuration
- [ ] Environment configuration management
- [ ] Database backup strategy
- [ ] Monitoring and alerting setup
- [ ] Deployment documentation
- [ ] Disaster recovery plan
- [ ] Production smoke tests

**Deliverables:**
- Production-ready application
- Security hardening complete
- Deployment automation
- Monitoring and alerting

---

## 6. Microservices Architecture Details

### 6.1 Service Module Structure

```
opsflow/
├── api/
│   ├── __init__.py
│   ├── dependencies.py      # Shared dependencies (DB, auth)
│   ├── middleware.py        # Request/response middleware
│   └── routes/
│       ├── __init__.py
│       ├── auth.py
│       ├── tasks.py
│       ├── sla.py
│       ├── reports.py
│       ├── audit.py
│       └── health.py
├── services/                # Business logic layer
│   ├── __init__.py
│   ├── auth_service.py      # Authentication logic
│   ├── task_service.py      # Task management
│   ├── sla_service.py       # SLA enforcement
│   ├── notification_service.py
│   ├── reporting_service.py
│   └── audit_service.py
├── workers/                 # Celery workers
│   ├── __init__.py
│   ├── celery_app.py
│   ├── sla_workers.py
│   ├── notification_workers.py
│   └── reporting_workers.py
├── models/                  # SQLAlchemy models
│   ├── __init__.py
│   ├── user.py
│   ├── task.py
│   ├── sla_event.py
│   ├── audit_log.py
│   └── notification.py
├── schemas/                 # Pydantic schemas
│   ├── __init__.py
│   ├── user.py
│   ├── task.py
│   ├── sla.py
│   └── common.py
├── core/                    # Core utilities
│   ├── __init__.py
│   ├── config.py
│   ├── security.py
│   ├── database.py
│   ├── redis.py
│   └── logging.py
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
└── main.py                  # Application entry point
```

### 6.2 Service Communication Pattern

Services communicate through well-defined interfaces:

```python
# Example: Task Service Interface
class TaskService:
    def __init__(self, db: Session, audit_service: AuditService,
                 sla_service: SLAService):
        self.db = db
        self.audit_service = audit_service
        self.sla_service = sla_service

    async def create_task(self, task_data: TaskCreate,
                          user: User) -> Task:
        """
        Creates task and triggers SLA scheduling
        """
        # 1. Create task in DB
        task = Task(**task_data.dict())
        self.db.add(task)
        self.db.commit()

        # 2. Log audit event
        await self.audit_service.log_action(
            entity_type="task",
            entity_id=task.id,
            action="TASK_CREATED",
            actor=user
        )

        # 3. Schedule SLA monitoring
        await self.sla_service.schedule_monitoring(task)

        return task
```

### 6.3 Event-Driven Communication

Services publish and subscribe to events via Redis:

```python
# Event publishing
class SLAService:
    async def detect_breach(self, task: Task):
        # Detect breach
        breach_event = self._create_breach_event(task)

        # Publish event
        await self.event_bus.publish(
            channel="sla.breach",
            event={
                "event_type": "SLA_BREACH",
                "task_id": str(task.id),
                "breach_type": "RESOLVE_BREACH",
                "timestamp": datetime.utcnow().isoformat()
            }
        )

# Event subscription
class NotificationService:
    async def subscribe_to_events(self):
        await self.event_bus.subscribe(
            channel="sla.breach",
            handler=self.handle_sla_breach
        )

    async def handle_sla_breach(self, event: dict):
        # Send notifications
        await self.send_breach_notification(event)
```

---

## 7. Background Worker Details

### 7.1 Celery Task Definitions

```python
# workers/sla_workers.py
from celery import Task
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

@celery_app.task(bind=True, max_retries=3)
def check_start_sla(self: Task, task_id: str):
    """
    Checks if task has been started within SLA
    """
    try:
        task = get_task(task_id)

        if task.status in ['CREATED', 'ASSIGNED']:
            # Task not started, create warning
            sla_event = create_sla_event(
                task_id=task_id,
                event_type='START_BREACH',
                severity='CRITICAL'
            )

            # Trigger notification
            send_notification.delay(
                task_id=task_id,
                event_id=sla_event.id,
                notification_type='START_BREACH'
            )

            # Schedule escalation
            escalate_task.apply_async(
                args=[task_id],
                countdown=300  # 5 minutes
            )

        logger.info(f"SLA check completed for task {task_id}")

    except Exception as exc:
        logger.error(f"SLA check failed: {exc}")
        raise self.retry(exc=exc, countdown=60)

@celery_app.task(bind=True, max_retries=3)
def check_resolve_sla(self: Task, task_id: str):
    """
    Checks if task has been resolved within SLA
    """
    # Similar to check_start_sla
    pass

@celery_app.task
def escalate_task(task_id: str):
    """
    Escalates task to admin
    """
    task = get_task(task_id)
    admin = get_admin_for_escalation()

    send_notification.delay(
        task_id=task_id,
        recipient_id=admin.id,
        notification_type='ESCALATION'
    )
```

### 7.2 Celery Beat Schedule

```python
# workers/celery_app.py
from celery.schedules import crontab

celery_app.conf.beat_schedule = {
    'refresh-dashboard-cache': {
        'task': 'workers.reporting_workers.refresh_dashboard',
        'schedule': 60.0,  # Every minute
    },
    'cleanup-old-logs': {
        'task': 'workers.maintenance_workers.cleanup_audit_logs',
        'schedule': crontab(hour=2, minute=0),  # 2 AM daily
    },
    'refresh-materialized-views': {
        'task': 'workers.reporting_workers.refresh_views',
        'schedule': crontab(minute='*/15'),  # Every 15 minutes
    },
}
```

---

## 8. Security Implementation

### 8.1 JWT Authentication

```python
# core/security.py
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
REFRESH_TOKEN_EXPIRE_DAYS = 7

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

### 8.2 RBAC Implementation

```python
# api/dependencies.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    token = credentials.credentials
    payload = verify_token(token)

    user = db.query(User).filter(User.id == payload["sub"]).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Invalid user")

    return user

def require_role(*allowed_roles: str):
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=403,
                detail=f"Insufficient permissions. Required: {allowed_roles}"
            )
        return current_user
    return role_checker

# Usage in routes
@router.post("/tasks")
async def create_task(
    task_data: TaskCreate,
    current_user: User = Depends(require_role("admin", "manager"))
):
    # Only admins and managers can create tasks
    pass
```

### 8.3 Rate Limiting

```python
# api/middleware.py
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import time

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, redis_client, requests_per_minute=60):
        super().__init__(app)
        self.redis = redis_client
        self.rpm = requests_per_minute

    async def dispatch(self, request: Request, call_next):
        # Get client identifier (user ID or IP)
        client_id = self._get_client_id(request)

        # Rate limit key
        key = f"rate_limit:{client_id}:{int(time.time() / 60)}"

        # Increment counter
        count = self.redis.incr(key)

        if count == 1:
            self.redis.expire(key, 60)

        if count > self.rpm:
            return JSONResponse(
                status_code=429,
                content={"error": "Rate limit exceeded"}
            )

        response = await call_next(request)
        response.headers["X-Rate-Limit-Limit"] = str(self.rpm)
        response.headers["X-Rate-Limit-Remaining"] = str(self.rpm - count)

        return response
```

---

## 9. Testing Strategy

### 9.1 Test Pyramid

```
        /\
       /  \  E2E Tests (5%)
      /----\
     / Inte-\
    / gration\ (25%)
   /---------\
  /   Unit    \
 /    Tests    \ (70%)
/_______________\
```

### 9.2 Unit Test Example

```python
# tests/unit/services/test_task_service.py
import pytest
from datetime import datetime, timedelta
from opsflow.services.task_service import TaskService
from opsflow.schemas.task import TaskCreate

@pytest.fixture
def task_service(db_session, mock_audit_service, mock_sla_service):
    return TaskService(
        db=db_session,
        audit_service=mock_audit_service,
        sla_service=mock_sla_service
    )

@pytest.mark.asyncio
async def test_create_task_schedules_sla_monitoring(
    task_service, admin_user, developer_user
):
    # Arrange
    task_data = TaskCreate(
        title="Test Task",
        task_type="TASK",
        priority="HIGH",
        assigned_to=developer_user.id,
        start_sla_minutes=30,
        resolve_sla_minutes=120
    )

    # Act
    task = await task_service.create_task(task_data, admin_user)

    # Assert
    assert task.id is not None
    assert task.status == "ASSIGNED"

    # Verify SLA service was called
    task_service.sla_service.schedule_monitoring.assert_called_once_with(task)

    # Verify audit log was created
    task_service.audit_service.log_action.assert_called_once()
```

### 9.3 Integration Test Example

```python
# tests/integration/test_task_lifecycle.py
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_complete_task_lifecycle(
    async_client: AsyncClient,
    admin_token: str,
    developer_token: str
):
    # Create task as admin
    response = await async_client.post(
        "/api/v1/tasks",
        json={
            "title": "Integration Test Task",
            "task_type": "TASK",
            "priority": "HIGH",
            "assigned_to": developer_user_id,
            "start_sla_minutes": 30,
            "resolve_sla_minutes": 120
        },
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 201
    task_id = response.json()["id"]

    # Start task as developer
    response = await async_client.patch(
        f"/api/v1/tasks/{task_id}/start",
        headers={"Authorization": f"Bearer {developer_token}"}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "IN_PROGRESS"

    # Complete task as developer
    response = await async_client.patch(
        f"/api/v1/tasks/{task_id}/complete",
        json={"resolution_notes": "Task completed successfully"},
        headers={"Authorization": f"Bearer {developer_token}"}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "COMPLETED"

    # Verify audit trail
    response = await async_client.get(
        f"/api/v1/audit-logs?entity_id={task_id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert len(response.json()["items"]) >= 3  # Create, Start, Complete
```

### 9.4 Load Test Example (k6)

```javascript
// tests/load/task_creation.js
import http from 'k6/http';
import { check, sleep } from 'k6';

export let options = {
    stages: [
        { duration: '30s', target: 20 },   // Ramp up
        { duration: '1m', target: 50 },    // Stay at 50 users
        { duration: '30s', target: 0 },    // Ramp down
    ],
    thresholds: {
        http_req_duration: ['p(95)<500'],  // 95% requests < 500ms
        http_req_failed: ['rate<0.01'],    // Error rate < 1%
    },
};

const BASE_URL = 'http://localhost:8000/api/v1';

export function setup() {
    // Login and get token
    let loginRes = http.post(`${BASE_URL}/auth/login`, JSON.stringify({
        username: 'admin',
        password: 'password'
    }), {
        headers: { 'Content-Type': 'application/json' },
    });

    return { token: loginRes.json('access_token') };
}

export default function(data) {
    let payload = JSON.stringify({
        title: `Load Test Task ${Date.now()}`,
        task_type: 'TASK',
        priority: 'MEDIUM',
        start_sla_minutes: 30,
        resolve_sla_minutes: 120
    });

    let params = {
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${data.token}`
        },
    };

    let res = http.post(`${BASE_URL}/tasks`, payload, params);

    check(res, {
        'status is 201': (r) => r.status === 201,
        'task created': (r) => r.json('id') !== undefined,
    });

    sleep(1);
}
```

---

## 10. Monitoring & Observability

### 10.1 Structured Logging

```python
# core/logging.py
import structlog
from pythonjsonlogger import jsonlogger

def configure_logging():
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

# Usage
logger = structlog.get_logger()

logger.info(
    "task_created",
    task_id=task.id,
    task_type=task.task_type,
    priority=task.priority,
    assigned_to=task.assigned_to,
    sla_minutes=task.resolve_sla_minutes
)
```

### 10.2 Prometheus Metrics

```python
# core/metrics.py
from prometheus_client import Counter, Histogram, Gauge, generate_latest

# Counters
tasks_created_total = Counter(
    'opsflow_tasks_created_total',
    'Total number of tasks created',
    ['task_type', 'priority']
)

sla_breaches_total = Counter(
    'opsflow_sla_breaches_total',
    'Total number of SLA breaches',
    ['breach_type']
)

# Histograms
task_completion_duration = Histogram(
    'opsflow_task_completion_duration_seconds',
    'Task completion time in seconds',
    ['task_type', 'priority']
)

# Gauges
active_tasks = Gauge(
    'opsflow_active_tasks',
    'Number of active tasks',
    ['status']
)

# Usage in service
def create_task(task_data):
    task = Task(**task_data.dict())
    db.add(task)
    db.commit()

    tasks_created_total.labels(
        task_type=task.task_type,
        priority=task.priority
    ).inc()

    active_tasks.labels(status='created').inc()

    return task
```

### 10.3 Grafana Dashboard Configuration

```json
{
  "dashboard": {
    "title": "OpsFlow Operations Dashboard",
    "panels": [
      {
        "title": "Active Tasks by Status",
        "type": "graph",
        "targets": [
          {
            "expr": "opsflow_active_tasks",
            "legendFormat": "{{status}}"
          }
        ]
      },
      {
        "title": "SLA Breach Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(opsflow_sla_breaches_total[5m])",
            "legendFormat": "{{breach_type}}"
          }
        ]
      },
      {
        "title": "Task Completion Time (p95)",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, opsflow_task_completion_duration_seconds_bucket)",
            "legendFormat": "{{task_type}}"
          }
        ]
      }
    ]
  }
}
```

---

## 11. Deployment Configuration

### 11.1 Docker Compose (Development)

```yaml
# docker-compose.yml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: opsflow
      POSTGRES_USER: opsflow
      POSTGRES_PASSWORD: opsflow_dev_pass
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U opsflow"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  api:
    build:
      context: .
      dockerfile: Dockerfile
    command: uvicorn opsflow.main:app --host 0.0.0.0 --port 8000 --reload
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://opsflow:opsflow_dev_pass@postgres:5432/opsflow
      REDIS_URL: redis://redis:6379/0
      JWT_SECRET_KEY: dev_secret_key_change_in_prod
      LOG_LEVEL: DEBUG
    volumes:
      - .:/app
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy

  celery_worker:
    build:
      context: .
      dockerfile: Dockerfile
    command: celery -A opsflow.workers.celery_app worker --loglevel=info
    environment:
      DATABASE_URL: postgresql://opsflow:opsflow_dev_pass@postgres:5432/opsflow
      REDIS_URL: redis://redis:6379/0
    depends_on:
      - postgres
      - redis
    volumes:
      - .:/app

  celery_beat:
    build:
      context: .
      dockerfile: Dockerfile
    command: celery -A opsflow.workers.celery_app beat --loglevel=info
    environment:
      DATABASE_URL: postgresql://opsflow:opsflow_dev_pass@postgres:5432/opsflow
      REDIS_URL: redis://redis:6379/0
    depends_on:
      - postgres
      - redis
    volumes:
      - .:/app

  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      GF_SECURITY_ADMIN_PASSWORD: admin
    volumes:
      - grafana_data:/var/lib/grafana
      - ./monitoring/grafana/dashboards:/etc/grafana/provisioning/dashboards
    depends_on:
      - prometheus

volumes:
  postgres_data:
  redis_data:
  prometheus_data:
  grafana_data:
```

### 11.2 Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 opsflow && \
    chown -R opsflow:opsflow /app

USER opsflow

EXPOSE 8000

CMD ["uvicorn", "opsflow.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 11.3 Nginx Configuration (Production)

```nginx
# nginx/opsflow.conf
upstream opsflow_api {
    least_conn;
    server api:8000 max_fails=3 fail_timeout=30s;
}

server {
    listen 80;
    server_name api.opsflow.io;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.opsflow.io;

    # SSL Configuration
    ssl_certificate /etc/nginx/ssl/opsflow.crt;
    ssl_certificate_key /etc/nginx/ssl/opsflow.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Security Headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # Rate Limiting
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=100r/m;
    limit_req zone=api_limit burst=20 nodelay;

    # Client body size limit
    client_max_body_size 10M;

    # Timeouts
    proxy_connect_timeout 60s;
    proxy_send_timeout 60s;
    proxy_read_timeout 60s;

    location /api/v1/ {
        proxy_pass http://opsflow_api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # CORS headers (if needed)
        add_header Access-Control-Allow-Origin * always;
        add_header Access-Control-Allow-Methods "GET, POST, PATCH, DELETE, OPTIONS" always;
        add_header Access-Control-Allow-Headers "Authorization, Content-Type" always;

        if ($request_method = OPTIONS) {
            return 204;
        }
    }

    location /health {
        proxy_pass http://opsflow_api/health;
        access_log off;
    }

    location /metrics {
        proxy_pass http://opsflow_api/metrics;

        # Restrict access to metrics
        allow 10.0.0.0/8;
        deny all;
    }
}
```

---

## 12. CI/CD Pipeline

### 12.1 GitHub Actions Workflow

```yaml
# .github/workflows/ci-cd.yml
name: OpsFlow CI/CD

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

env:
  PYTHON_VERSION: '3.11'
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  lint-and-format:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ env.PYTHON_VERSION }}

      - name: Install dependencies
        run: |
          pip install black flake8 isort mypy bandit

      - name: Run Black
        run: black --check .

      - name: Run isort
        run: isort --check-only .

      - name: Run Flake8
        run: flake8 . --max-line-length=100 --exclude=migrations

      - name: Run MyPy
        run: mypy opsflow --ignore-missing-imports

      - name: Run Bandit (Security)
        run: bandit -r opsflow -ll

  test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:15-alpine
        env:
          POSTGRES_DB: opsflow_test
          POSTGRES_USER: test
          POSTGRES_PASSWORD: test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

      redis:
        image: redis:7-alpine
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 6379:6379

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ env.PYTHON_VERSION }}

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-dev.txt

      - name: Run tests with coverage
        env:
          DATABASE_URL: postgresql://test:test@localhost:5432/opsflow_test
          REDIS_URL: redis://localhost:6379/0
          JWT_SECRET_KEY: test_secret
        run: |
          pytest tests/ -v --cov=opsflow --cov-report=xml --cov-report=term

      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage.xml
          fail_ci_if_error: true

  security-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Run Safety check
        run: |
          pip install safety
          safety check --json

      - name: Run OWASP Dependency Check
        uses: dependency-check/Dependency-Check_Action@main
        with:
          project: 'OpsFlow'
          path: '.'
          format: 'HTML'

  build-and-push:
    needs: [lint-and-format, test, security-scan]
    runs-on: ubuntu-latest
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'

    permissions:
      contents: read
      packages: write

    steps:
      - uses: actions/checkout@v3

      - name: Log in to Container Registry
        uses: docker/login-action@v2
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v4
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}

      - name: Build and push Docker image
        uses: docker/build-push-action@v4
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}

  deploy-staging:
    needs: build-and-push
    runs-on: ubuntu-latest
    environment: staging

    steps:
      - name: Deploy to staging
        run: |
          echo "Deploying to staging environment"
          # Add deployment commands here

  smoke-tests:
    needs: deploy-staging
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Run smoke tests
        run: |
          pip install httpx pytest
          pytest tests/smoke/ -v
        env:
          API_BASE_URL: https://staging-api.opsflow.io

  deploy-production:
    needs: smoke-tests
    runs-on: ubuntu-latest
    environment: production
    if: github.ref == 'refs/heads/main'

    steps:
      - name: Deploy to production
        run: |
          echo "Deploying to production environment"
          # Add production deployment commands
```

---

## 13. Key Implementation Files

### 13.1 Main Application Entry Point

```python
# opsflow/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from prometheus_client import make_asgi_app

from opsflow.api.routes import (
    auth, tasks, sla, reports, audit, health
)
from opsflow.api.middleware import (
    RateLimitMiddleware, RequestLoggingMiddleware,
    ErrorHandlingMiddleware
)
from opsflow.core.config import settings
from opsflow.core.logging import configure_logging
from opsflow.core.database import engine
from opsflow.models import Base

# Configure logging
configure_logging()

# Create FastAPI app
app = FastAPI(
    title="OpsFlow API",
    description="Event-Driven Task & SLA Enforcement Backend",
    version="1.0.0",
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc",
    openapi_url="/api/v1/openapi.json"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Custom middleware
app.add_middleware(ErrorHandlingMiddleware)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(
    RateLimitMiddleware,
    redis_client=redis_client,
    requests_per_minute=settings.RATE_LIMIT_PER_MINUTE
)

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(tasks.router, prefix="/api/v1/tasks", tags=["Tasks"])
app.include_router(sla.router, prefix="/api/v1/sla-events", tags=["SLA"])
app.include_router(reports.router, prefix="/api/v1/reports", tags=["Reports"])
app.include_router(audit.router, prefix="/api/v1/audit-logs", tags=["Audit"])
app.include_router(health.router, prefix="", tags=["Health"])

# Prometheus metrics endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    # Create database tables
    Base.metadata.create_all(bind=engine)
    logger.info("Application started successfully")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on application shutdown"""
    logger.info("Application shutting down")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "opsflow.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
```

---

## 14. Production Checklist

### Pre-Deployment

- [ ] All tests passing (unit, integration, E2E)
- [ ] Code coverage > 80%
- [ ] Security scan completed (no critical vulnerabilities)
- [ ] Load testing completed (meets performance targets)
- [ ] Database migrations tested
- [ ] Environment variables configured
- [ ] SSL certificates installed
- [ ] Monitoring dashboards configured
- [ ] Alerting rules defined
- [ ] Backup strategy implemented
- [ ] Disaster recovery plan documented

### Post-Deployment

- [ ] Smoke tests passing
- [ ] Health endpoints responding
- [ ] Metrics being collected
- [ ] Logs aggregating correctly
- [ ] Celery workers running
- [ ] SLA timers triggering correctly
- [ ] Notifications sending successfully
- [ ] Database connections stable
- [ ] Redis cache working

---

## 15. Resume Impact Metrics

To quantify the project impact on a resume:

**Technical Metrics:**
- Built event-driven backend handling **1,000+ concurrent SLA timers**
- Achieved **<100ms P95 latency** for task operations
- Maintained **99.9% uptime** for SLA enforcement
- Processed **10K+ background jobs daily** with retry mechanisms
- Implemented **role-based access control** for 3 user roles
- Achieved **>85% code coverage** with comprehensive test suite

**Business Metrics:**
- Reduced **SLA breach rate by 40%** through automated monitoring
- Eliminated **100% of manual escalations** via autonomous system
- Decreased **mean-time-to-resolution by 35%** with proactive alerts
- Provided **real-time visibility** into operational metrics
- Created **audit trails** for compliance and accountability

---

## Conclusion

This development plan provides a complete blueprint for building OpsFlow as a production-grade, event-driven operations backend. The microservices-style architecture ensures maintainability and future scalability, while the comprehensive testing and observability strategies guarantee reliability and operational excellence.

The 12-week timeline is aggressive but achievable with focused execution. Each phase builds upon the previous one, ensuring continuous delivery of value while maintaining high quality standards.