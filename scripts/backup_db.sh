#!/bin/bash
# ==============================================================================
# MediLoop Automated Database & Media Backup Script
# Creates timestamped compressed backups of PostgreSQL DB and upload files.
# ==============================================================================

set -e

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_DIR="./backups/${TIMESTAMP}"
CONTAINER_DB_NAME="mediloop-db"
DB_USER="postgres"
DB_NAME="mediloop"

echo "=== Starting MediLoop Backup [${TIMESTAMP}] ==="

mkdir -p "${BACKUP_DIR}"

# 1. Backup PostgreSQL Database Schema & Data
echo "[1/2] Exporting PostgreSQL Database Dump..."
docker exec -t ${CONTAINER_DB_NAME} pg_dump -U ${DB_USER} -d ${DB_NAME} -F c -b -v -f /tmp/mediloop_${TIMESTAMP}.dump
docker cp ${CONTAINER_DB_NAME}:/tmp/mediloop_${TIMESTAMP}.dump "${BACKUP_DIR}/mediloop_db.dump"
docker exec -t ${CONTAINER_DB_NAME} rm /tmp/mediloop_${TIMESTAMP}.dump

# 2. Backup Uploaded Prescription Images
echo "[2/2] Archiving Prescription Upload Images..."
if [ -d "backend/uploads/prescriptions" ]; then
    tar -czf "${BACKUP_DIR}/prescription_uploads.tar.gz" -C backend/uploads/prescriptions .
fi

echo "=== Backup Completed Successfully! ==="
echo "Backup Archive Location: ${BACKUP_DIR}"
