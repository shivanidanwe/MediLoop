# 🎬 MediLoop v1.0 — End-to-End Demonstration & UAT Script

This document provides a step-by-step demonstration script for live user acceptance testing (UAT), capstone presentations, and academic evaluations of **MediLoop v1.0**.

---

## 🎭 Roles Involved

1. **Patient (User)**: Uses the Flutter Mobile App.
2. **Pharmacist (Admin)**: Uses the React Dashboard Console.
3. **MediLoop AI Engine**: Background multi-agent workflow system.

---

## 📋 12-Step Demonstration Walkthrough

### Step 1: Patient Registration & Authentication
- **Action**: Open the Flutter app, navigate to `RegisterScreen`, enter details (Name, Email, Password, Gender, Relationship).
- **Verification**: User is registered in PostgreSQL, receives a JWT access token, and lands on `HomeScreen`.

### Step 2: Profile & Medical History Setup
- **Action**: Go to `ProfileScreen` ➔ Add Medical Information (e.g., "Penicillin Allergy", "Hypertension").
- **Verification**: Profile record is updated in database for downstream AI safety checks.

### Step 3: Browse Catalog & Medicine Search
- **Action**: Search for "Crocin 650" or filter by "Pain Relief".
- **Verification**: Instant search results loaded from `/api/v1/medicines`.

### Step 4: Prescription Scanner Upload
- **Action**: Navigate to `UploadPrescriptionScreen` ➔ Select prescription image ➔ Click **Upload**.
- **Verification**: Image is validated (<=10MB, JPG/PNG/PDF), sanitized on disk, and created in database with `PROCESSING` status.

### Step 5: Multi-Agent AI Pipeline Execution
- **Action**: Backend automatically executes `MultiAgentWorkflowEngine`:
  - `OCRAgent` extracts text.
  - `PrescriptionIntelligenceAgent` parses medicines (`Paracetamol 500mg`).
  - `MedicineMatchingAgent` maps to SKU.
  - `DrugSafetyAgent` evaluates patient allergy profile.
- **Verification**: `DrugSafetyAgent` detects allergy/safety flag or proceeds to recommendation.

### Step 6: Human-in-the-Loop Pharmacist Review (If Flagged)
- **Action**: If a safety flag is raised, workflow enters `WAITING_FOR_REVIEW`. Open React Dashboard (`Prescriptions` tab).
- **Verification**: Pharmacist views OCR text, safety warnings, and clicks **Approve** with notes.

### Step 7: Workflow Resume & Auto-Cart Population
- **Action**: Pharmacist approval triggers `engine.resume_workflow(...)` ➔ `OrderRecommendationAgent` auto-populates the customer's cart in Flutter.
- **Verification**: Customer receives notification; opening `CartScreen` displays auto-recommended prescribed medicines.

### Step 8: Cart Checkout & Order Placement
- **Action**: Patient selects delivery address on `CartScreen` and clicks **Place Order**.
- **Verification**: Order is created in PostgreSQL with status `PLACED`.

### Step 9: Pharmacist Order Fulfillment
- **Action**: Switch to React Dashboard (`Orders` tab) ➔ Locate new order ➔ Change status from `PLACED` to `DISPATCHED` ➔ `DELIVERED`.
- **Verification**: Stock quantity decreases in `PharmacyInventory`.

### Step 10: Automated Refill Reminder Trigger
- **Action**: Backend `order_completed` event fires `RefillReminderAgent` ➔ calculates adherence schedule.
- **Verification**: Notification generated for patient's scheduled refill date.

### Step 11: AI Health Companion Interaction
- **Action**: Patient opens `AIChatScreen` ➔ Types *"I have a fever, what should I take?"* or *"Help me refill my prescription"*.
- **Verification**: `AIHealthCompanionAgent` calls `/api/v1/ai/chat`, returning medical guidance and medicine recommendations.

### Step 12: System Audit Trail & Telemetry Verification
- **Action**: Open `/api/v1/ai/telemetry` in browser/Postman.
- **Verification**: View structured JSON telemetry metrics showing workflow execution times, step statuses, and zero active errors.
