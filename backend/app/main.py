import os
import logging
from fastapi import FastAPI, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

# Import database core and engine
from app.core.database import engine, Base
from app.core.rate_limiter import RateLimiterMiddleware
from app.core.audit_logger import log_audit_event

# Import all models to ensure they are registered with Base.metadata before calling create_all
from app.models.user import User
from app.models.address import Address
from app.models.medical_info import MedicalInfo
from app.models.emergency_contact import EmergencyContact
from app.models.pharmacy import Pharmacy
from app.models.pharmacist import Pharmacist
from app.models.prescription import Prescription, PrescriptionItem
from app.models.medicine import Medicine
from app.models.pharmacy_inventory import PharmacyInventory
from app.models.cart import Cart, CartItem
from app.models.order import Order, OrderItem
from app.models.notification import Notification
from app.models.purchase_order import SupplierPurchaseOrder

# Auto-create database tables
Base.metadata.create_all(bind=engine)

# Import routes
from app.api import auth, users, pharmacies, pharmacists, prescriptions, medicines, orders, notifications, ai, inventory, cart, orchestration

logger = logging.getLogger(__name__)

# Initialize FastAPI Application
app = FastAPI(
    title="MediLoop Backend API",
    description="MediLoop Backend - AI-Driven Healthcare & Autonomous Pharmacy Platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Custom Security Headers Middleware
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response

# Configure Security & Middleware Layers
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RateLimiterMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static directory for uploaded prescriptions safely
os.makedirs("uploads/prescriptions", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Global Exception Handler (Masking internal tracebacks from public clients)
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception(f"Unhandled exception on {request.method} {request.url.path}: {str(exc)}")
    log_audit_event(
        event_type="UNHANDLED_EXCEPTION",
        action=f"{request.method} {request.url.path}",
        status="FAILURE",
        details={"error": str(exc)}
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "An internal server error occurred. Please contact support.",
            "error_code": "INTERNAL_SERVER_ERROR"
        }
    )

# Register API Routers under the /api/v1 prefix
app.include_router(auth.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(pharmacies.router, prefix="/api/v1")
app.include_router(pharmacists.router, prefix="/api/v1")
app.include_router(prescriptions.router, prefix="/api/v1")
app.include_router(medicines.router, prefix="/api/v1")
app.include_router(inventory.router, prefix="/api/v1")
app.include_router(cart.router, prefix="/api/v1")
app.include_router(orders.router, prefix="/api/v1")
app.include_router(notifications.router, prefix="/api/v1")
app.include_router(ai.router, prefix="/api/v1")
app.include_router(orchestration.router, prefix="/api/v1")
app.include_router(orchestration.router, prefix="/api")

# Base health & root endpoints
@app.get("/")
def read_root():
    return {"message": "MediLoop API Running (Secure Production Environment)"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "security": "hardened"}
