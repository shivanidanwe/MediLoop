"""
MediLoop Medicine Matching Agent.
Matches extracted prescription medicine entries against the MediLoop catalog database.
"""
import difflib
import re
from typing import Any, Dict, List, Optional, Tuple
from app.agents.base_agent import BaseAgent
from app.agents.context import AgentContext
from app.agents.events import AgentEvent
from app.agents.exceptions import AgentValidationError


# Reference catalog for standalone matching (syncs with database query fallback)
MEDILOOP_CATALOG: List[Dict[str, Any]] = [
    {"id": 1, "brand_name": "Crocin 650", "generic_name": "Paracetamol", "strength": "650 mg", "manufacturer": "GSK", "price": 32.50},
    {"id": 2, "brand_name": "Crocin 500", "generic_name": "Paracetamol", "strength": "500 mg", "manufacturer": "GSK", "price": 28.00},
    {"id": 3, "brand_name": "Dolo 650", "generic_name": "Paracetamol", "strength": "650 mg", "manufacturer": "Micro Labs", "price": 30.00},
    {"id": 4, "brand_name": "Calpol 500", "generic_name": "Paracetamol", "strength": "500 mg", "manufacturer": "GSK", "price": 25.00},
    {"id": 5, "brand_name": "Amoxil 500", "generic_name": "Amoxicillin", "strength": "500 mg", "manufacturer": "GSK", "price": 85.00},
    {"id": 6, "brand_name": "Mox 250", "generic_name": "Amoxicillin", "strength": "250 mg", "manufacturer": "Sun Pharma", "price": 55.00},
    {"id": 7, "brand_name": "Augmentin 625", "generic_name": "Amoxicillin + Clavulanic Acid", "strength": "625 mg", "manufacturer": "GSK", "price": 210.00},
    {"id": 8, "brand_name": "Lipitor 10", "generic_name": "Atorvastatin", "strength": "10 mg", "manufacturer": "Pfizer", "price": 140.00},
    {"id": 9, "brand_name": "Atorva 10", "generic_name": "Atorvastatin", "strength": "10 mg", "manufacturer": "Zydus", "price": 95.00},
    {"id": 10, "brand_name": "Glucophage 500", "generic_name": "Metformin", "strength": "500 mg", "manufacturer": "Merck", "price": 60.00},
    {"id": 11, "brand_name": "Glycomet 500", "generic_name": "Metformin", "strength": "500 mg", "manufacturer": "USV", "price": 42.00},
    {"id": 12, "brand_name": "Shelcal 500", "generic_name": "Calcium + Vitamin D3", "strength": "500 mg", "manufacturer": "Torrent", "price": 115.00},
    {"id": 13, "brand_name": "Zyrtec 10", "generic_name": "Cetirizine", "strength": "10 mg", "manufacturer": "UCB Pharma", "price": 38.00},
    {"id": 14, "brand_name": "Azee 500", "generic_name": "Azithromycin", "strength": "500 mg", "manufacturer": "Cipla", "price": 125.00},
    {"id": 47, "brand_name": "Ceftas-O 200", "generic_name": "Cefixime + Ofloxacin", "strength": "200 mg + 200 mg", "manufacturer": "Intas Pharmaceuticals", "price": 145.00},
    {"id": 48, "brand_name": "Drotin-DS", "generic_name": "Drotaverine Hydrochloride", "strength": "80 mg", "manufacturer": "Walter Bushnell", "price": 135.00},
    {"id": 49, "brand_name": "Acera-D", "generic_name": "Rabeprazole + Domperidone", "strength": "20 mg + 30 mg", "manufacturer": "Ipca Laboratories", "price": 110.00},
    {"id": 50, "brand_name": "Alkarate Liquid", "generic_name": "Disodium Hydrogen Citrate", "strength": "1.4 g / 5 ml", "manufacturer": "Wallace Pharmaceuticals", "price": 115.00},
]

# Medical Brand & Abbreviation to Generic Mapping (Level 3 & Level 6)
BRAND_ABBREVIATION_MAP: Dict[str, str] = {
    "pcm": "Paracetamol",
    "crocin": "Paracetamol",
    "calpol": "Paracetamol",
    "dolo": "Paracetamol",
    "paracetamol": "Paracetamol",
    "amox": "Amoxicillin",
    "amoxil": "Amoxicillin",
    "mox": "Amoxicillin",
    "amoxicillin": "Amoxicillin",
    "amoxycillin": "Amoxicillin",
    "ceftas": "Cefixime + Ofloxacin",
    "ceftas-o": "Cefixime + Ofloxacin",
    "drotin": "Drotaverine Hydrochloride",
    "drotin-ds": "Drotaverine Hydrochloride",
    "drotac": "Drotaverine Hydrochloride",
    "drotac-ds": "Drotaverine Hydrochloride",
    "acera": "Rabeprazole + Domperidone",
    "acera-d": "Rabeprazole + Domperidone",
    "alkasafe": "Disodium Hydrogen Citrate",
    "alkarate": "Disodium Hydrogen Citrate",
    "lipitor": "Atorvastatin",
    "atorva": "Atorvastatin",
    "atorvastatin": "Atorvastatin",
    "glucophage": "Metformin",
    "glycomet": "Metformin",
    "metformin": "Metformin",
    "shelcal": "Calcium + Vitamin D3",
    "vitamin d3": "Calcium + Vitamin D3",
    "zyrtec": "Cetirizine",
    "cetrizine": "Cetirizine",
    "cetirizine": "Cetirizine",
    "azi": "Azithromycin",
    "azee": "Azithromycin",
    "azithromycin": "Azithromycin",
    "hcqs": "Hydroxychloroquine",
}


class MedicineMatchingAgent(BaseAgent):
    """
    Agent responsible for matching extracted prescription medicines against the
    application's catalog database using a 6-level intelligent matching pipeline.
    """

    def __init__(self, catalog: Optional[List[Dict[str, Any]]] = None):
        self.catalog = catalog or MEDILOOP_CATALOG

    @property
    def name(self) -> str:
        return "medicine_matching_agent"

    @property
    def description(self) -> str:
        return (
            "Matches extracted prescription medicine entries against the catalog database "
            "using multi-level matching (exact, case-insensitive, brand-to-generic, "
            "fuzzy spelling, strength normalization, and abbreviation mappings)."
        )

    @property
    def handled_events(self) -> List[AgentEvent]:
        return [
            AgentEvent.MEDICINES_EXTRACTED,
            AgentEvent.OCR_COMPLETED,
            AgentEvent.PRESCRIPTION_UPLOADED,
        ]

    async def can_handle(self, event: AgentEvent, context: AgentContext) -> bool:
        """
        Agent can handle when extracted_medicines contains entries.
        """
        return event in self.handled_events and len(context.extracted_medicines) > 0

    async def validate(self, context: AgentContext) -> bool:
        """
        Validates that extracted_medicines is non-empty before matching.
        """
        if not context.extracted_medicines:
            raise AgentValidationError(
                "MedicineMatchingAgent validation failed: 'extracted_medicines' is empty in context."
            )
        return True

    async def execute(self, context: AgentContext) -> AgentContext:
        """
        Processes context.extracted_medicines and updates context.matched_medicines & metadata.
        """
        extracted = context.extracted_medicines or []
        matched_results: List[Dict[str, Any]] = []

        # Dynamically load live catalog from database if available
        if getattr(context, "db", None):
            try:
                from app.models.medicine import Medicine
                from app.models.pharmacy_inventory import PharmacyInventory
                db_meds = context.db.query(Medicine).filter(Medicine.is_active == True).all()
                if db_meds:
                    new_cat = []
                    for m in db_meds:
                        inv = context.db.query(PharmacyInventory).filter(PharmacyInventory.medicine_id == m.id).first()
                        p = float(inv.selling_price) if inv and inv.selling_price else 45.0
                        new_cat.append({
                            "id": m.id,
                            "brand_name": m.brand_name,
                            "generic_name": m.generic_name,
                            "strength": m.strength,
                            "dosage_form": m.dosage_form,
                            "manufacturer": m.manufacturer,
                            "price": p,
                        })
                    self.catalog = new_cat
            except Exception:
                pass

        for item in extracted:
            raw_name = item.get("name", "")
            raw_strength = item.get("strength", "")
            dosage = item.get("dosage", "")
            frequency = item.get("frequency", "")
            duration = item.get("duration", "")
            quantity = item.get("quantity") or "10"

            matched_item = self._match_single_medicine(raw_name, raw_strength)
            if matched_item:
                # Inherit dosage, frequency, duration, and quantity from prescription context
                matched_item["dosage"] = dosage
                matched_item["frequency"] = frequency
                matched_item["duration"] = duration
                matched_item["quantity"] = quantity
                matched_results.append(matched_item)
            else:
                # Add warning for unmatched medicine
                context.add_warning(
                    f"Unable to match medicine '{raw_name}' in catalog inventory."
                )
                # Find fuzzy alternative recommendations
                alternatives = self._find_alternatives(raw_name)
                matched_results.append({
                    "id": None,
                    "name": raw_name,
                    "generic_name": "Unmatched",
                    "strength": raw_strength,
                    "dosage": dosage,
                    "frequency": frequency,
                    "duration": duration,
                    "manufacturer": "Unknown",
                    "price": 0.0,
                    "confidence": 0.0,
                    "match_level": "UNMATCHED",
                    "alternatives": alternatives,
                })

        context.matched_medicines = matched_results
        context.metadata["medicine_matching"] = {
            "total_items": len(extracted),
            "matched_items": sum(1 for m in matched_results if m["confidence"] > 0.0),
            "unmatched_items": sum(1 for m in matched_results if m["confidence"] == 0.0),
            "status": "SUCCESS" if matched_results else "NO_ITEMS",
        }

        return context

    def _match_single_medicine(self, raw_name: str, raw_strength: str) -> Optional[Dict[str, Any]]:
        """
        Executes 6-level matching pipeline for a raw medicine name & strength.
        """
        clean_input = raw_name.strip()
        norm_input = clean_input.lower()
        norm_strength = self._normalize_strength(raw_strength)

        # Level 1: Exact Match (Brand or Generic)
        for item in self.catalog:
            if clean_input == item["brand_name"] or clean_input == item["generic_name"]:
                return self._format_match(item, confidence=0.99, level="Level 1: Exact Match")

        # Level 2: Case-Insensitive Match
        for item in self.catalog:
            if norm_input == item["brand_name"].lower() or norm_input == item["generic_name"].lower():
                return self._format_match(item, confidence=0.95, level="Level 2: Case-Insensitive Match")

        # Level 3 & Level 6: Brand ↔ Generic & Abbreviation Resolution
        input_first_word = norm_input.split()[0] if norm_input else ""
        mapped_generic = BRAND_ABBREVIATION_MAP.get(norm_input) or BRAND_ABBREVIATION_MAP.get(input_first_word)
        if mapped_generic:
            # Find best catalog item matching resolved generic name + strength
            matches = [i for i in self.catalog if i["generic_name"].lower() == mapped_generic.lower()]
            if matches:
                # Prefer item matching normalized strength
                best_match = next((i for i in matches if self._normalize_strength(i["strength"]) == norm_strength), matches[0])
                conf = 0.93 if norm_strength and self._normalize_strength(best_match["strength"]) == norm_strength else 0.88
                return self._format_match(best_match, confidence=conf, level="Level 3: Brand/Abbrev Mapping")

        # Level 4: Fuzzy Spelling Match
        all_names = []
        name_to_item = {}
        for item in self.catalog:
            b_name = item["brand_name"].lower()
            g_name = item["generic_name"].lower()
            all_names.extend([b_name, g_name])
            name_to_item[b_name] = item
            name_to_item[g_name] = item

        close_matches = difflib.get_close_matches(norm_input, all_names, n=1, cutoff=0.70)
        if close_matches:
            best_item = name_to_item[close_matches[0]]
            ratio = difflib.SequenceMatcher(None, norm_input, close_matches[0]).ratio()
            return self._format_match(best_item, confidence=round(ratio * 0.92, 2), level="Level 4: Fuzzy Match")

        # Level 5: Substring / Partial Name + Strength Match
        for item in self.catalog:
            if input_first_word and (input_first_word in item["brand_name"].lower() or input_first_word in item["generic_name"].lower()):
                return self._format_match(item, confidence=0.75, level="Level 5: Substring Match")

        return None

    def _normalize_strength(self, strength: str) -> str:
        """Standardizes strength string (e.g. '650mg' -> '650 mg')."""
        if not strength:
            return ""
        s = strength.lower().strip()
        s = re.sub(r'(\d+)\s*(mg|g|mcg|ml|iu|%)', r'\1 \2', s)
        return s

    def _find_alternatives(self, raw_name: str) -> List[Dict[str, Any]]:
        """Returns top alternative recommendations from catalog."""
        norm_input = raw_name.lower()
        alts = []
        for item in self.catalog:
            ratio = difflib.SequenceMatcher(None, norm_input, item["brand_name"].lower()).ratio()
            if ratio > 0.40:
                alts.append({
                    "id": item["id"],
                    "name": item["brand_name"],
                    "generic_name": item["generic_name"],
                    "price": item["price"],
                    "confidence": round(ratio, 2)
                })

        alts.sort(key=lambda x: x["confidence"], reverse=True)
        return alts[:3]

    def _format_match(self, item: Dict[str, Any], confidence: float, level: str) -> Dict[str, Any]:
        """Formats catalog match dictionary."""
        alternatives = self._find_alternatives(item["brand_name"])
        # Exclude exact self from alternatives
        alternatives = [a for a in alternatives if a["id"] != item["id"]]

        return {
            "id": item["id"],
            "name": item["brand_name"],
            "generic_name": item["generic_name"],
            "strength": item["strength"],
            "manufacturer": item["manufacturer"],
            "price": item["price"],
            "confidence": confidence,
            "match_level": level,
            "alternatives": alternatives[:2],
        }
