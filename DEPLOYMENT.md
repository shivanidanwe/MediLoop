# MediLoop Enterprise Deployment & Operations Guide

This guide details the complete production deployment procedures for the **MediLoop Healthcare Platform**, including Docker Compose containerization, Nginx gateway configuration, database backup/recovery, and CI/CD pipelines.

---

## 🏗️ System Architecture

```text
[ Mobile / Web Clients ]
           │
           ▼
[ Nginx Reverse Proxy Gateway (Port 80/443) ]
     │                              │
     ▼                              ▼
[ React Dashboard (Port 80) ]   [ FastAPI Backend (Port 8000) ]
                                    │
                                    ▼
                         [ PostgreSQL 16 DB (Port 5432) ]
```

---

## ⚙️ Prerequisites

- **Docker**: Engine version 24.0+ and Docker Compose v2.20+
- **Git**: 2.40+
- **RAM**: Minimum 4GB system memory (8GB recommended for concurrent AI workloads)

---

## 🚀 Quickstart Deployment

### 1. Environment Setup
Copy `.env.example` to `.env` and fill in secrets:
```bash
cp .env.example .env
```

### 2. Launch Container Stack
Start all services in detached production mode:
```bash
docker-compose up -d --build
```

### 3. Verify Container Health
Check container status:
```bash
docker-compose ps
```

Verify backend health API:
```bash
curl http://localhost/health
```

---

## 💾 Backup & Disaster Recovery

### Automated Database Backup
Execute the backup script to dump PostgreSQL database schemas and uploaded images:
```bash
chmod +x scripts/backup_db.sh
./scripts/backup_db.sh
```

### Database Restore Procedure
To restore PostgreSQL from a `.dump` archive:
```bash
docker cp backups/YYYYMMDD_HHMMSS/mediloop_db.dump mediloop-db:/tmp/restore.dump
docker exec -it mediloop-db pg_restore -U postgres -d mediloop -c /tmp/restore.dump
```

---

## 🔍 Monitoring & Telemetry

- **API Documentation**: `http://localhost/api/docs`
- **AI Agent Telemetry Endpoint**: `http://localhost/api/v1/ai/telemetry`
- **Application Logs**:
  ```bash
  docker-compose logs -f backend
  ```
