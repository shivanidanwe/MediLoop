"""
MediLoop Autonomous Procurement Agent.
Monitors inventory depletion post-prescription approval, analyzes stock deficits,
calculates optimal reorder quantities, and generates ready-to-dispatch Supplier Invoices & Purchase Orders.
"""
import uuid
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session

from app.agents.base_agent import BaseAgent
from app.agents.context import AgentContext
from app.agents.events import AgentEvent
from app.models.purchase_order import SupplierPurchaseOrder
from app.models.pharmacy import Pharmacy
from app.models.medicine import Medicine
from app.models.pharmacy_inventory import PharmacyInventory

logger = logging.getLogger(__name__)

PRIMARY_SUPPLIER = {
    "name": "Apex Healthcare & Pharma Distributors Pvt Ltd",
    "email": "procurement@apexpharma.in",
    "phone": "+91 98450 88990",
    "address": "Plot 42, Karnataka Industrial Area, Peenya 2nd Stage, Bengaluru - 560058",
    "gstin": "29AABCU9603R1ZX",
    "drug_license": "KA-BLR-DL-2022-99881"
}


class ProcurementAgent(BaseAgent):
    """
    Autonomous agent responsible for generating supplier replenishment invoices
    when pharmacy stock becomes depleted or falls below safety thresholds.
    """

    @property
    def name(self) -> str:
        return "procurement_agent"

    @property
    def description(self) -> str:
        return (
            "Analyzes low or depleted pharmacy inventory post-verification and generates "
            "formal Supplier Invoices & Purchase Orders ready for distributor dispatch."
        )

    @property
    def handled_events(self) -> List[AgentEvent]:
        return [
            AgentEvent.LOW_STOCK_DETECTED,
            AgentEvent.PRESCRIPTION_VERIFIED,
            AgentEvent.INVENTORY_CHECKED
        ]

    async def can_handle(self, event: AgentEvent, context: AgentContext) -> bool:
        return event in self.handled_events

    async def validate(self, context: AgentContext) -> bool:
        return True

    async def execute(self, context: AgentContext) -> AgentContext:
        """
        Executes multi-agent workflow context update if invoked through workflow engine.
        """
        return context

    @classmethod
    def generate_supplier_invoice(
        cls,
        db: Session,
        pharmacy_id: int,
        low_stock_items: List[Dict[str, Any]],
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generates and saves a formal Purchase Order / Supplier Invoice for depleted or low-stock medicines.
        
        low_stock_items format:
        [
            {
                "medicine_id": 1,
                "medicine_name": "Paracetamol 500mg",
                "current_stock": 2,
                "threshold": 15,
                "recommended_order_qty": 100, # optional, will calculate if missing
                "unit_price": 45.0 # optional, estimated wholesale price calculated
            }
        ]
        """
        pharmacy = db.query(Pharmacy).filter(Pharmacy.id == pharmacy_id).first()
        pharmacy_name = pharmacy.pharmacy_name if pharmacy else f"Pharmacy #{pharmacy_id}"
        pharmacy_address = pharmacy.address if pharmacy else "Local Network Hub"

        po_code = f"PO-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        
        line_items = []
        subtotal = 0.0

        for item in low_stock_items:
            med_id = item.get("medicine_id")
            med_name = item.get("medicine_name") or "Prescribed Medication"
            current_stock = item.get("current_stock", 0)
            
            # Lookup DB medicine details if possible
            if med_id:
                med_record = db.query(Medicine).filter(Medicine.id == med_id).first()
                if med_record and not med_name:
                    med_name = f"{med_record.brand_name} ({med_record.strength})"

            # Dynamic reorder sizing: if 0 stock -> 100 units, if <= 10 -> 60 units
            order_qty = item.get("recommended_order_qty")
            if not order_qty:
                order_qty = 100 if current_stock <= 0 else 60

            # Wholesale cost is typically 65-70% of retail price
            retail_price = item.get("unit_price") or 50.0
            wholesale_unit_price = round(retail_price * 0.70, 2)
            line_total = round(order_qty * wholesale_unit_price, 2)
            subtotal += line_total

            line_items.append({
                "medicine_id": med_id,
                "medicine_name": med_name,
                "current_stock": current_stock,
                "reorder_quantity": order_qty,
                "unit_wholesale_price": wholesale_unit_price,
                "line_total": line_total,
                "recommended_batch": f"BATCH-{datetime.now().strftime('%m%y')}-{uuid.uuid4().hex[:4].upper()}",
                "urgency": "CRITICAL - OUT OF STOCK" if current_stock <= 0 else "HIGH - LOW STOCK"
            })

        gst_tax = round(subtotal * 0.12, 2) # Standard 12% GST on pharmaceuticals
        grand_total = round(subtotal + gst_tax, 2)

        default_notes = (
            f"Autonomous Replenishment Invoice created by MediLoop Procurement Agent. "
            f"Fulfillment requested for {pharmacy_name} due to active prescription demand."
        )

        # Persist PO in PostgreSQL database
        db_po = SupplierPurchaseOrder(
            po_number=po_code,
            pharmacy_id=pharmacy_id,
            supplier_name=PRIMARY_SUPPLIER["name"],
            supplier_email=PRIMARY_SUPPLIER["email"],
            supplier_phone=PRIMARY_SUPPLIER["phone"],
            status="READY_FOR_SUPPLIER",
            items_json=line_items,
            subtotal=subtotal,
            tax_amount=gst_tax,
            total_amount=grand_total,
            notes=notes or default_notes
        )
        db.add(db_po)
        db.commit()
        db.refresh(db_po)

        logger.info(
            f"ProcurementAgent: Supplier Purchase Order {po_code} generated for "
            f"{len(line_items)} items. Total: Rs.{grand_total} (Pharmacy: {pharmacy_name})"
        )

        return {
            "id": db_po.id,
            "po_number": db_po.po_number,
            "status": db_po.status,
            "created_at": db_po.created_at.isoformat() if db_po.created_at else datetime.now().isoformat(),
            "pharmacy": {
                "id": pharmacy_id,
                "name": pharmacy_name,
                "address": pharmacy_address
            },
            "supplier": PRIMARY_SUPPLIER,
            "line_items": line_items,
            "subtotal": subtotal,
            "tax_amount": gst_tax,
            "total_amount": grand_total,
            "notes": db_po.notes,
            "action_ready": "SEND_TO_SUPPLIER"
        }
