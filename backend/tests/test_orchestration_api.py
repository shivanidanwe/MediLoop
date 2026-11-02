"""
MediLoop Multi-Agent Orchestration Layer - API Integration Test Suite.
Tests all FastAPI REST endpoints mounted under /api/v1/orchestration and /api/orchestration.
"""
import os
import sys
import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app
from app.core.database import SessionLocal
from app.models.prescription import Prescription

client = TestClient(app)


def test_api_list_agents():
    """Tests GET /api/v1/orchestration/agents and /api/orchestration/agents."""
    res = client.get("/api/v1/orchestration/agents")
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 6
    agent_ids = [a["agent_id"] for a in data]
    assert "ocr_agent" in agent_ids
    assert "procurement_agent" in agent_ids

    # Check unversioned alias endpoint
    res2 = client.get("/api/orchestration/agents")
    assert res2.status_code == 200
    assert len(res2.json()) == 6


def test_api_agent_status():
    """Tests GET /api/v1/orchestration/agents/{agent_id}/status."""
    res = client.get("/api/v1/orchestration/agents/ocr_agent/status")
    assert res.status_code == 200
    data = res.json()
    assert data["agent"]["agent_id"] == "ocr_agent"
    assert "is_healthy" in data


def test_api_procurement_recommendations():
    """Tests GET /api/v1/orchestration/procurement/recommendations."""
    res = client.get("/api/v1/orchestration/procurement/recommendations?pharmacy_id=1")
    assert res.status_code == 200
    assert isinstance(res.json(), list)


def test_api_refill_predictions():
    """Tests GET /api/v1/orchestration/refill/predictions."""
    res = client.get("/api/v1/orchestration/refill/predictions")
    assert res.status_code == 200
    assert isinstance(res.json(), list)


def test_api_prescription_process_flow():
    """Tests end-to-end HTTP pipeline trigger and extraction checkpoint."""
    db = SessionLocal()
    # Find a prescription with valid extracted text or our test user's prescription
    rx = db.query(Prescription).filter(Prescription.extracted_text != None).order_by(Prescription.id.desc()).first()
    if not rx:
        rx = db.query(Prescription).first()
    db.close()

    if not rx:
        pytest.skip("No prescription in database to test HTTP pipeline trigger.")

    # 1. Process prescription pipeline
    res = client.post(f"/api/v1/orchestration/prescriptions/{rx.id}/process?auto_order=false")
    assert res.status_code == 200
    wf_data = res.json()
    assert "workflow_id" in wf_data

    # 2. Query extraction checkpoint
    res_ext = client.get(f"/api/v1/orchestration/prescriptions/{rx.id}/extraction")
    assert res_ext.status_code == 200
    ext_data = res_ext.json()
    assert ext_data["prescription_id"] == rx.id

    # 3. Query safety assessment
    res_safety = client.get(f"/api/v1/orchestration/prescriptions/{rx.id}/safety")
    assert res_safety.status_code == 200
    safety_data = res_safety.json()
    assert safety_data["prescription_id"] == rx.id

    # 4. Re-evaluate safety
    res_reeval = client.post(
        f"/api/v1/orchestration/prescriptions/{rx.id}/safety/re-evaluate",
        json={"cleared_by_pharmacist": True, "pharmacist_notes": "Clinical review verified OK."}
    )
    assert res_reeval.status_code == 200
    assert res_reeval.json()["can_proceed"] == True
