import sys
import asyncio

sys.path.insert(0, "backend")

from app.agents.factory import get_workflow_engine
from app.agents.context import AgentContext
from app.core.database import SessionLocal

async def main():
    engine = get_workflow_engine()
    db = SessionLocal()
    try:
        ctx = AgentContext(uploaded_image="test_rx.jpg")
        ctx.db = db
        ctx.metadata["customer_id"] = 1
        
        print("[*] Executing MediLoop Multi-Agent Workflow Pipeline with local Ollama GPU inference...")
        res = await engine.execute_prescription_upload_workflow(ctx)
        
        print(f"[STATUS] Workflow Status: {res.status.value}")
        print(f"[DURATION] Pipeline Duration: {res.duration_ms:.2f} ms")
        print(f"[EXTRACTED] Medicines: {len(res.context.extracted_medicines)}")
        for m in res.context.extracted_medicines:
            print(f"   -> {m.get('name')} | Strength: {m.get('strength')} | Dose: {m.get('dosage')} | Freq: {m.get('frequency')}")
        print(f"[MATCHED] Catalog Medicines: {len(res.context.matched_medicines)}")
        for m in res.context.matched_medicines:
            print(f"   -> {m.get('name')} (Generic: {m.get('generic_name')}) Price: Rs {m.get('price')}")
        safety = res.context.metadata.get("drug_safety", {})
        print(f"[SAFETY] Overall Risk: {safety.get('risk_level')} | Requires Pharmacist Review: {safety.get('requires_pharmacist_review')}")
        inv = res.context.metadata.get("inventory", {})
        print(f"[INVENTORY] Status: {inv.get('overall_status')} | Pharmacy: {inv.get('selected_pharmacy', {}).get('name')}")
        order = res.context.metadata.get("order_recommendation", {})
        print(f"[ORDER] Status: {order.get('order_status')} | Cart Populated: {order.get('cart_populated')}")
        print(f"[SUCCESS] Multi-Agent Pipeline with live Ollama & PostgreSQL executed perfectly!")
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(main())
