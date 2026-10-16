# MediLoop Backend Foundation

This is the backend foundation for **MediLoop - AI Driven Agentic Ordering and Autonomous Pharmacy System**.

## Tech Stack
* Python 3.11+
* FastAPI
* PostgreSQL
* SQLAlchemy ORM
* Pydantic
* JWT Authentication
* Uvicorn

---

## Setup Instructions

### 1. Prerequisites
Ensure you have Python 3.11+ installed.

### 2. Create and Activate Virtual Environment
```bash
# Navigate to the backend directory
cd backend

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows (PowerShell):
.venv\Scripts\Activate.ps1
# On Windows (CMD):
.venv\Scripts\activate.bat
# On macOS/Linux:
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configuration
Copy the `.env.example` file to `.env` and fill in your settings:
```bash
cp .env.example .env
```
Make sure to create a PostgreSQL database named `mediloop` and update `DATABASE_URL` in `.env` to match your local credentials.

### 5. Running the Application
To run the server in development mode with hot-reloading:
```bash
uvicorn app.main:app --reload
```

The API will be available at:
* API Root: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
* Health Endpoint: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)
* Interactive Swagger Docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
* Redoc: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
