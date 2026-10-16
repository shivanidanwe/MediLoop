# 🩺 MediLoop — Agentic AI Healthcare & Autonomous Pharmacy Platform

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/shivanidanwe/MediLoop)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)]()
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-009688.svg)](https://fastapi.tiangolo.com)
[![Flutter](https://img.shields.io/badge/Flutter-3.29.0-02569B.svg)](https://flutter.dev)
[![React](https://img.shields.io/badge/React-18.0-61DAFB.svg)](https://reactjs.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16.0-336791.svg)](https://www.postgresql.org)

**MediLoop** is a production-grade, end-to-end **Agentic AI Healthcare & Autonomous Pharmacy Platform**. It combines a premium Flutter mobile application for patients, an operational React dashboard for pharmacists, a FastAPI & PostgreSQL backend, and an autonomous **10-Agent AI Workflow Engine** for prescription OCR, clinical drug safety verification, inventory matching, and automated refill tracking.

---

## 🏛️ System Architecture

```text
                               ┌──────────────────────────┐
                               │  Flutter Mobile App      │
                               │  (Patient Mobile Portal) │
                               └────────────┬─────────────┘
                                            │ HTTP / REST
                                            ▼
┌──────────────────────────┐   ┌──────────────────────────┐
│  React Dashboard         │──►│  Nginx Reverse Proxy     │
│  (Pharmacist Console)    │   │  Gateway (Port 80)       │
└──────────────────────────┘   └────────────┬─────────────┘
                                            │
                                            ▼
                               ┌──────────────────────────┐
                               │  FastAPI Backend Service │
                               │  (Port 8000)             │
                               └────────────┬─────────────┘
                                            │
               ┌────────────────────────────┼────────────────────────────┐
               │                            │                            │
               ▼                            ▼                            ▼
┌──────────────────────────┐  ┌──────────────────────────┐  ┌──────────────────────────┐
│ PostgreSQL 16 Database   │  │ 10-Agent AI Engine       │  │ Encrypted Disk Storage   │
│ (Users, Orders, Items)   │  │ (LangGraph / Async)      │  │ (Uploads & Prescriptions)│
└──────────────────────────┘  └──────────────────────────┘  └──────────────────────────┘
```

---

## 🤖 Multi-Agent AI Architecture

MediLoop features an autonomous **Multi-Agent Workflow Engine** (`backend/app/agents/`) that processes prescriptions and user requests through 10 specialized AI agents:

| Agent Name | Primary Responsibility |
| :--- | :--- |
| **1. OCR Agent** | Extracts raw text and confidence scores from uploaded prescription images/PDFs. |
| **2. Prescription Intelligence Agent** | Parses raw OCR text into structured medicine names, strengths, dosages, and frequencies. |
| **3. Medicine Matching Agent** | Performs fuzzy string matching against database inventory to map parsed items to actual SKUs. |
| **4. Drug Safety Agent** | Evaluates patient medical history for drug-drug interactions, penicillin/NSAID allergies, and dosage safety. |
| **5. Inventory Availability Agent** | Checks real-time stock levels, batch expiry dates, and warehouse availability. |
| **6. Order Recommendation Agent** | Assembles final order items, applies discounts, and auto-populates the customer's active cart. |
| **7. Refill Reminder Agent** | Calculates adherence schedules and predicts when patients require automated refills. |
| **8. Notification Agent** | Generates push notifications, SMS alerts, and in-app messages. |
| **9. AI Health Companion Agent** | Conversational health assistant answering patient queries (`/ai/chat`) with clinical disclaimers. |
| **10. Pharmacist Review Agent** | Manages human-in-the-loop state pauses (`WAITING_FOR_REVIEW`) for high-risk safety alerts. |

---

## 📱 Component Stack

### 1. Flutter Mobile Application (`/lib`)
- **State Management**: Provider Pattern
- **UI/UX**: Custom Material 3 dynamic glassmorphism design system with dark mode, animations, and micro-interactions
- **Key Features**: Prescription Scanner, AI Health Chat, Medicine Search, Cart & Order Checkout, Order Tracking, Profile & Prescription Management

### 2. React Pharmacist Dashboard (`/pharmacy dashboard`)
- **Tech Stack**: React 18, Vite, Lucide Icons, Axios
- **Key Features**: Real-time Order Monitoring, Prescription Manual Review Console, Inventory CRUD Management, Customer Insights, Analytics & Reports

### 3. FastAPI Backend (`/backend`)
- **Tech Stack**: Python 3.12, FastAPI, SQLAlchemy ORM, Pydantic v2, Passlib (bcrypt), PyJWT
- **Key Features**: JWT Authentication (Patient & Pharmacist), File Upload Security (10MB limit, MIME checks), Rate Limiting, Audit Logging, Async Background Tasks

### 4. Database Layer
- **Engine**: PostgreSQL 16
- **Models**: `User`, `Address`, `MedicalInfo`, `Pharmacy`, `Pharmacist`, `Prescription`, `Medicine`, `PharmacyInventory`, `Cart`, `Order`, `Notification`

---

## ⚙️ Quickstart & Local Setup

### Prerequisites
- Flutter SDK (3.29.0+)
- Python (3.12+)
- Node.js (20+)
- PostgreSQL (16+) or Docker Desktop

### 1. Environment Setup
Copy the configuration template:
```bash
cp .env.example .env
```

### 2. Backend Setup
```bash
cd backend
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. React Dashboard Setup
```bash
cd pharmacy-dashboard
npm install
npm run dev
```

### 4. Flutter Mobile App Setup
```bash
flutter pub get
flutter run
```

---

## 🐳 Docker Production Deployment

To launch the complete containerized stack (FastAPI, PostgreSQL 16, React Dashboard, and Nginx Gateway):

```bash
docker-compose up -d --build
```

Access services at:
- **Nginx Web Gateway**: `http://localhost`
- **FastAPI API Docs**: `http://localhost/api/docs`
- **React Pharmacist Dashboard**: `http://localhost`

---

## 🧪 Testing & Verification

### Backend Pytest Suite
```bash
cd backend
pytest -v
```
*(Runs 16 unit, security, and performance benchmark tests)*

### Flutter Test Suite
```bash
flutter test
```
*(Runs 10 mobile unit, service, and widget tests)*

---

## 🔒 Security Hardening

- **JWT Authentication & RBAC**: Enforces role-based permissions (Patient vs Pharmacist).
- **File Upload Protection**: 10MB file size limit, extension validation (`.jpg`, `.jpeg`, `.png`, `.pdf`), and UUID disk sanitization.
- **Sliding Window Rate Limiter**: Protects auth, upload, and AI chat endpoints against DoS.
- **Security HTTP Headers**: `X-Content-Type-Options`, `X-Frame-Options`, `X-XSS-Protection`, `HSTS`.
- **Log Data Redaction**: Automatic masking of passwords, JWT tokens, and sensitive PII in server logs.

---

## 📄 License & Credits

Developed as an enterprise-grade Capstone Project. Licensed under the MIT License.
