"""
MediLoop Inventory Availability Agent.
Evaluates pharmacy inventory availability, stock quantities, expiry dates,
and alternative pharmacy fulfillment options without altering database stock.
"""
from datetime import datetime, timedelta
import re
from typing import Any, Dict, List, Optional
from app.agents.base_agent import BaseAgent
from app.agents.context import AgentContext
from app.agents.events import AgentEvent
from app.agents.exceptions import AgentValidationError


# Default Pharmacy Network Catalog
PHARMACY_NETWORK: List[Dict[str, Any]] = [
    {"id": 1, "name": "MediLoop Central Pharmacy", "address": "123 Healthcare Blvd", "is_active": True, "rating": 4.9},
    {"id": 2, "name": "Apollo Pharmacy - Express Branch", "address": "45 MG Road", "is_active": True, "rating": 4.7},
    {"id": 3, "name": "MedPlus Pharmacy", "address": "78 Station Road", "is_active": True, "rating": 4.6},
]

# Pharmacy Inventory Database Mapping
PHARMACY_INVENTORY: Dict[int, List[Dict[str, Any]]] = {
    1: [  # MediLoop Central Pharmacy
        {"medicine_id": 1, "name": "Crocin 650", "stock": 150, "price": 32.50, "expiry": "2027-12-31"},
        {"medicine_id": 2, "name": "Crocin 500", "stock": 80, "price": 28.00, "expiry": "2027-08-30"},
        {"medicine_id": 5, "name": "Amoxil 500", "stock": 45, "price": 85.00, "expiry": "2027-05-15"},
        {"medicine_id": 8, "name": "Lipitor 10", "stock": 60, "price": 140.00, "expiry": "2026-11-20"},
        {"medicine_id": 10, "name": "Glucophage 500", "stock": 0, "price": 60.00, "expiry": "2026-08-10"},  # Out of stock
        {"medicine_id": 12, "name": "Shelcal 500", "stock": 100, "price": 115.00, "expiry": "2027-10-01"},
    ],
    2: [  # Apollo Pharmacy - Express Branch
        {"medicine_id": 1, "name": "Crocin 650", "stock": 200, "price": 32.50, "expiry": "2027-12-31"},
        {"medicine_id": 5, "name": "Amoxil 500", "stock": 100, "price": 85.00, "expiry": "2027-05-15"},
        {"medicine_id": 8, "name": "Lipitor 10", "stock": 90, "price": 140.00, "expiry": "2026-11-20"},
        {"medicine_id": 10, "name": "Glucophage 500", "stock": 50, "price": 60.00, "expiry": "2027-09-15"},  # In stock
        {"medicine_id": 12, "name": "Shelcal 500", "stock": 120, "price": 115.00, "expiry": "2027-10-01"},
    ],
    3: [  # MedPlus Pharmacy
        {"medicine_id": 1, "name": "Crocin 650", "stock": 50, "price": 32.50, "expiry": "2027-12-31"},
        {"medicine_id": 10, "name": "Glucophage 500", "stock": 30, "price": 60.00, "expiry": "2027-09-15"},
    ],
}


class InventoryAvailabilityAgent(BaseAgent):
    """
    Agent responsible for analyzing stock availability, expiry validation,
    and alternative pharmacy fulfillment options without reserving or altering stock.
    """

    def __init__(
        self,
        pharmacies: Optional[List[Dict[str, Any]]] = None,
        inventory: Optional[Dict[int, List[Dict[str, Any]]]] = None,
        min_shelf_days: int = 30,
    ):
        self.pharmacies = pharmacies or PHARMACY_NETWORK
        self.inventory = inventory or PHARMACY_INVENTORY
        self.min_shelf_days = min_shelf_days

    @property
    def name(self) -> str:
        return "inventory_availability_agent"

    @property
    def description(self) -> str:
        return (
            "Evaluates inventory availability, stock quantities, expiry dates, "
            "and alternative pharmacy fulfillment options for matched prescription medicines."
        )

    @property
    def handled_events(self) -> List[AgentEvent]:
        return [
            AgentEvent.SAFETY_VALIDATION_COMPLETED,
            AgentEvent.MEDICINES_MATCHED,
            AgentEvent.MEDICINES_EXTRACTED,
            AgentEvent.OCR_COMPLETED,
            AgentEvent.PRESCRIPTION_UPLOADED,
        ]

    async def can_handle(self, event: AgentEvent, context: AgentContext) -> bool:
        """
        Handles event if matched_medicines or extracted_medicines exists.
        """
        has_matched = len(context.matched_medicines) > 0
        has_extracted = len(context.extracted_medicines) > 0
        return event in self.handled_events and (has_matched or has_extracted)

    async def validate(self, context: AgentContext) -> bool:
        """
        Validates presence of medicine records in context.
        """
        if not context.matched_medicines and not context.extracted_medicines:
            raise AgentValidationError(
                "InventoryAvailabilityAgent validation failed: No medicines available in context."
            )
        return True

    async def execute(self, context: AgentContext) -> AgentContext:
        """
        Analyzes pharmacy stock and populates context.metadata['inventory'].
        """
        target_medicines = context.matched_medicines if context.matched_medicines else context.extracted_medicines
        selected_pharmacy_id = int(context.pharmacy_id) if context.pharmacy_id else 1
        pharmacy_info = next((p for p in self.pharmacies if p["id"] == selected_pharmacy_id), self.pharmacies[0])
        current_inv = self.inventory.get(selected_pharmacy_id, [])

        # Live query from PostgreSQL if context.db is available
        if getattr(context, "db", None):
            try:
                from app.models.pharmacy_inventory import PharmacyInventory
                from app.models.pharmacy import Pharmacy
                db_pharm = context.db.query(Pharmacy).filter(
                    (Pharmacy.id == selected_pharmacy_id) if context.pharmacy_id else (Pharmacy.is_active == True)
                ).first()
                if db_pharm:
                    pharmacy_info = {
                        "id": db_pharm.id,
                        "name": db_pharm.pharmacy_name,
                        "address": db_pharm.address,
                        "is_active": True,
                        "rating": 4.9
                    }
                    db_items = context.db.query(PharmacyInventory).filter(
                        PharmacyInventory.pharmacy_id == db_pharm.id
                    ).all()
                    if db_items:
                        current_inv = [
                            {
                                "medicine_id": item.medicine_id,
                                "name": getattr(item.medicine, "brand_name", f"Medicine {item.medicine_id}"),
                                "stock": item.stock_quantity,
                                "price": item.selling_price,
                                "expiry": item.expiry_date.strftime("%Y-%m-%d") if item.expiry_date else "2027-12-31"
                            }
                            for item in db_items
                        ]
            except Exception:
                pass

        item_reports: List[Dict[str, Any]] = []
        unavailable_items: List[Dict[str, Any]] = []
        alternative_medicines: List[Dict[str, Any]] = []

        total_requested = len(target_medicines)
        fully_available_count = 0

        for med in target_medicines:
            med_id = med.get("id")
            raw_name = med.get("name", "Unknown")
            requested_qty = self._parse_requested_qty(med.get("quantity") or med.get("duration"))

            inv_record = self._find_in_inventory(current_inv, med_id, raw_name)
            available_qty = inv_record.get("stock", 0) if inv_record else 0
            expiry_str = inv_record.get("expiry", "2027-12-31") if inv_record else ""
            expiry_ok = self._validate_expiry(expiry_str)

            if inv_record and available_qty >= requested_qty and expiry_ok:
                status = "AVAILABLE"
                fully_available_count += 1
            elif inv_record and available_qty > 0 and expiry_ok:
                status = "PARTIAL"
                context.add_warning(
                    f"Insufficient stock for '{raw_name}' at {pharmacy_info['name']}. Requested: {requested_qty}, Available: {available_qty}."
                )
            else:
                status = "UNAVAILABLE"
                unavailable_items.append({
                    "medicine_id": med_id,
                    "name": raw_name,
                    "requested_quantity": requested_qty,
                    "available_quantity": available_qty,
                    "reason": "Out of Stock" if available_qty == 0 else "Nearing Expiry",
                })
                context.add_warning(
                    f"Item '{raw_name}' is UNAVAILABLE at {pharmacy_info['name']}."
                )

            # Collect generic alternatives if available in matched_medicines
            if med.get("alternatives"):
                alternative_medicines.extend(med["alternatives"])

            item_reports.append({
                "medicine_id": med_id,
                "name": raw_name,
                "requested_quantity": requested_qty,
                "available_quantity": available_qty,
                "status": status,
                "expiry_ok": expiry_ok,
                "unit_price": inv_record.get("price", med.get("price", 0.0)) if inv_record else 0.0,
            })

        complete_order = (fully_available_count == total_requested)
        if complete_order:
            overall_status = "AVAILABLE"
        elif fully_available_count > 0:
            overall_status = "PARTIAL_FULFILLMENT"
        else:
            overall_status = "UNAVAILABLE"

        # Search Alternative Pharmacies if selected pharmacy cannot fulfill 100%
        alternative_pharmacies = []
        if not complete_order:
            alternative_pharmacies = self._rank_alternative_pharmacies(
                target_medicines, exclude_pharmacy_id=selected_pharmacy_id
            )

        inventory_report = {
            "overall_status": overall_status,
            "complete_order": complete_order,
            "selected_pharmacy": pharmacy_info,
            "items": item_reports,
            "unavailable_items": unavailable_items,
            "alternative_pharmacies": alternative_pharmacies,
            "alternative_medicines": alternative_medicines[:3],
            "requires_manual_review": not complete_order,
        }

        context.metadata["inventory"] = inventory_report

        if not complete_order and alternative_pharmacies:
            top_alt = alternative_pharmacies[0]
            context.add_recommendation(
                f"Consider ordering from '{top_alt['pharmacy_name']}' which offers {top_alt['fulfillment_percentage']}% prescription fulfillment."
            )

        return context

    def _find_in_inventory(
        self, inventory: List[Dict[str, Any]], med_id: Optional[int], name: str
    ) -> Optional[Dict[str, Any]]:
        """Finds inventory item by ID or name matching."""
        if med_id:
            for item in inventory:
                if item.get("medicine_id") == med_id:
                    return item

        norm_name = name.lower()
        for item in inventory:
            if item.get("name", "").lower() in norm_name or norm_name in item.get("name", "").lower():
                return item
        return None

    def _validate_expiry(self, expiry_str: str) -> bool:
        """Validates remaining shelf life is above minimum threshold."""
        if not expiry_str:
            return True
        try:
            exp_date = datetime.strptime(expiry_str, "%Y-%m-%d")
            cutoff = datetime.now() + timedelta(days=self.min_shelf_days)
            return exp_date >= cutoff
        except Exception:
            return True

    def _parse_requested_qty(self, qty_val: Any) -> int:
        """Parses quantity string into integer quantity."""
        if isinstance(qty_val, int) and qty_val > 0:
            return qty_val
        if isinstance(qty_val, str):
            match = re.search(r'(\d+)', qty_val)
            if match:
                return int(match.group(1))
        return 10  # Default standard prescription pack quantity

    def _rank_alternative_pharmacies(
        self, medicines: List[Dict[str, Any]], exclude_pharmacy_id: int
    ) -> List[Dict[str, Any]]:
        """Ranks network pharmacies by complete stock fulfillment percentage."""
        rankings = []
        for pharm in self.pharmacies:
            if pharm["id"] == exclude_pharmacy_id or not pharm.get("is_active"):
                continue

            p_id = pharm["id"]
            p_inv = self.inventory.get(p_id, [])
            available_count = 0

            for med in medicines:
                med_id = med.get("id")
                raw_name = med.get("name", "")
                req_qty = self._parse_requested_qty(med.get("quantity"))
                inv_rec = self._find_in_inventory(p_inv, med_id, raw_name)

                if inv_rec and inv_rec.get("stock", 0) >= req_qty and self._validate_expiry(inv_rec.get("expiry", "")):
                    available_count += 1

            fulfillment_pct = round((available_count / len(medicines)) * 100.0, 1) if medicines else 0.0
            rankings.append({
                "pharmacy_id": p_id,
                "pharmacy_name": pharm["name"],
                "address": pharm["address"],
                "rating": pharm["rating"],
                "fulfillment_percentage": fulfillment_pct,
                "available_items_count": available_count,
                "total_items_count": len(medicines),
            })

        rankings.sort(key=lambda x: (x["fulfillment_percentage"], x["rating"]), reverse=True)
        return rankings
