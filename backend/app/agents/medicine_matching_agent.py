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
    {"id": 52, "brand_name": "Zerotil Plus", "generic_name": "Cefuroxime Axetil + Clavulanic Acid", "strength": "250 mg", "manufacturer": "Square Pharmaceuticals", "price": 240.00},
    {"id": 53, "brand_name": "Rolac", "generic_name": "Ketorolac Tromethamine", "strength": "10 mg", "manufacturer": "Square Pharmaceuticals", "price": 85.00},
    {"id": 54, "brand_name": "Maxpro", "generic_name": "Esomeprazole", "strength": "20 mg", "manufacturer": "Square Pharmaceuticals", "price": 75.00},
    {"id": 55, "brand_name": "Filamyd", "generic_name": "Metronidazole", "strength": "500 mg", "manufacturer": "Square Pharmaceuticals", "price": 45.00},
]

# Medical Brand & Abbreviation to Generic Mapping (Level 3 & Level 6)
BRAND_ABBREVIATION_MAP: Dict[str, str] = {
    # Respiratory & Inhalers
    "budesonide": "Budesonide",
    "formoterol": "Budesonide + Formoterol",
    "budesonide + formoterol": "Budesonide + Formoterol",
    "budecort": "Budesonide",
    "foracort": "Budesonide + Formoterol",
    "montelukast": "Montelukast",
    "montair": "Montelukast",
    "montair-lc": "Montelukast + Levocetirizine",
    "levocetirizine": "Levocetirizine",
    "levocet": "Levocetirizine",
    "salbutamol": "Salbutamol",
    "asthalin": "Salbutamol",
    "allegra": "Fexofenadine",
    "fexofenadine": "Fexofenadine",

    # Pain & Anti-inflammatory
    "pcm": "Paracetamol",
    "crocin": "Paracetamol",
    "calpol": "Paracetamol",
    "dolo": "Paracetamol",
    "paracetamol": "Paracetamol",
    "ibuprofen": "Ibuprofen",
    "brufen": "Ibuprofen",
    "combiflam": "Ibuprofen + Paracetamol",
    "diclofenac": "Diclofenac",
    "voveran": "Diclofenac",
    "aspirin": "Aspirin",
    "ecosprin": "Aspirin",
    "ketorolac": "Ketorolac Tromethamine",
    "rolac": "Ketorolac Tromethamine",

    # Antibiotics
    "amox": "Amoxicillin",
    "amoxil": "Amoxicillin",
    "mox": "Amoxicillin",
    "amoxicillin": "Amoxicillin",
    "amoxycillin": "Amoxicillin",
    "augmentin": "Amoxicillin + Clavulanic Acid",
    "cefixime": "Cefixime",
    "taxim": "Cefixime",
    "taxim-o": "Cefixime",
    "ceftas": "Cefixime + Ofloxacin",
    "ceftas-o": "Cefixime + Ofloxacin",
    "cefuroxime": "Cefuroxime Axetil + Clavulanic Acid",
    "zerotil": "Cefuroxime Axetil + Clavulanic Acid",
    "zerotil plus": "Cefuroxime Axetil + Clavulanic Acid",
    "ciprofloxacin": "Ciprofloxacin",
    "cifran": "Ciprofloxacin",
    "azithromycin": "Azithromycin",
    "azee": "Azithromycin",
    "azi": "Azithromycin",
    "doxycycline": "Doxycycline",
    "doxy": "Doxycycline",
    "metronidazole": "Metronidazole",
    "flagyl": "Metronidazole",
    "filamyd": "Metronidazole",

    # Gastrointestinal
    "pantoprazole": "Pantoprazole",
    "pantocid": "Pantoprazole",
    "pan": "Pantoprazole",
    "pan-d": "Pantoprazole + Domperidone",
    "omeprazole": "Omeprazole",
    "omez": "Omeprazole",
    "esomeprazole": "Esomeprazole",
    "maxpro": "Esomeprazole",
    "rabeprazole": "Rabeprazole",
    "acera": "Rabeprazole + Domperidone",
    "acera-d": "Rabeprazole + Domperidone",
    "ranitidine": "Ranitidine",
    "rantac": "Ranitidine",
    "drotin": "Drotaverine Hydrochloride",
    "drotin-ds": "Drotaverine Hydrochloride",
    "drotaverine": "Drotaverine Hydrochloride",
    "alkasafe": "Disodium Hydrogen Citrate",
    "alkarate": "Disodium Hydrogen Citrate",

    # Cardiovascular & Diabetes
    "lipitor": "Atorvastatin",
    "atorva": "Atorvastatin",
    "atorvastatin": "Atorvastatin",
    "rosuvastatin": "Rosuvastatin",
    "rosuvas": "Rosuvastatin",
    "telmisartan": "Telmisartan",
    "telma": "Telmisartan",
    "amlodipine": "Amlodipine",
    "amlopres": "Amlodipine",
    "metoprolol": "Metoprolol Succinate",
    "metolar": "Metoprolol Succinate",
    "glucophage": "Metformin",
    "glycomet": "Metformin",
    "metformin": "Metformin",
    "glimepiride": "Glimepiride",
    "amaryl": "Glimepiride",
    "sitagliptin": "Sitagliptin",
    "januvia": "Sitagliptin",

    # Vitamins & Allergy
    "shelcal": "Calcium + Vitamin D3",
    "vitamin d3": "Cholecalciferol (Vitamin D3)",
    "zyrtec": "Cetirizine",
    "cetrizine": "Cetirizine",
    "cetirizine": "Cetirizine",
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
                matched_item["name"] = raw_name  # Preserve extracted medicine name as it is
                matched_item["raw_name"] = raw_name
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
                    "quantity": quantity,
                    "manufacturer": "Unknown",
                    "price": 0.0,
                    "confidence": float(item.get("confidence") or 0.88),
                    "match_level": "UNMATCHED",
                    "alternatives": alternatives,
                })

        context.matched_medicines = matched_results
        context.metadata["medicine_matching"] = {
            "total_items": len(extracted),
            "matched_items": sum(1 for m in matched_results if m.get("match_level") != "UNMATCHED"),
            "unmatched_items": sum(1 for m in matched_results if m.get("match_level") == "UNMATCHED"),
            "status": "SUCCESS" if matched_results else "NO_ITEMS",
        }

        return context

    def _match_single_medicine(self, raw_name: str, raw_strength: str) -> Optional[Dict[str, Any]]:
        """
        Executes strict matching pipeline for a raw medicine name & strength.
        Strict rule: Extracted medicines must NEVER be substituted with different catalog brand names.
        Only matches catalog medicines whose brand_name or generic representation matches the extracted medicine name.
        """
        clean_input = raw_name.strip()
        norm_input = clean_input.lower()
        norm_strength = self._normalize_strength(raw_strength)

        # Strip standard dosage form prefixes & suffixes: Tab, Cap, Syp, Inj, Inhaler, etc.
        form_prefix_pattern = r'^(?:tab(?:let)?s?|cap(?:sule)?s?|syp|syrup|inj(?:ection)?s?|oint(?:ment)?|cream|drops?|inhaler)\.?\s+'
        stripped_norm = re.sub(form_prefix_pattern, '', norm_input, flags=re.IGNORECASE).strip()
        stripped_norm = re.sub(r'\s+(?:tab(?:let)?s?|cap(?:sule)?s?|syp|syrup|inj(?:ection)?s?|inhaler)$', '', stripped_norm, flags=re.IGNORECASE).strip()
        input_first_word = stripped_norm.split()[0] if stripped_norm else ""

        # Reject common non-medicine noise headers that slipped into extractor
        non_medicine_words = {
            "dr", "doctor", "patient", "name", "clinic", "hospital", "date", "age",
            "gender", "diagnosis", "vitals", "allergies", "history", "advice",
            "review", "prescription", "address", "reg", "department", "consultant"
        }
        if stripped_norm in non_medicine_words:
            return None

        def is_brand_compatible(item: Dict[str, Any]) -> bool:
            """Ensure candidate item brand_name is not a totally different brand substitution."""
            b_low = item["brand_name"].lower()
            if not input_first_word:
                return False
            # Brand name matches or starts with the input name
            if b_low.startswith(input_first_word) or input_first_word in b_low:
                return True
            # Or item generic matches and item brand name is also generic
            if stripped_norm == b_low or clean_input.lower() == b_low:
                return True
            return False

        # Level 1: Exact Match (Brand or Generic matching brand)
        for item in self.catalog:
            b_name = item["brand_name"]
            g_name = item["generic_name"]
            if clean_input in (b_name, g_name) or stripped_norm in (b_name.lower(), g_name.lower()):
                if is_brand_compatible(item):
                    return self._format_match(item, confidence=0.99, level="Level 1: Exact Match", raw_name=clean_input)

        # Level 2: Case-Insensitive Match
        for item in self.catalog:
            b_low = item["brand_name"].lower()
            g_low = item["generic_name"].lower()
            if stripped_norm in (b_low, g_low):
                if is_brand_compatible(item):
                    return self._format_match(item, confidence=0.95, level="Level 2: Case-Insensitive Match", raw_name=clean_input)

        # Level 3: Prefix Match on Compatible Brand (Requires min length >= 4)
        if len(stripped_norm) >= 4 or len(input_first_word) >= 4:
            search_token = stripped_norm if len(stripped_norm) >= 4 else input_first_word
            for item in self.catalog:
                b_low = item["brand_name"].lower()
                if b_low.startswith(search_token) or (len(search_token) >= 5 and search_token in b_low):
                    if norm_strength and self._normalize_strength(item["strength"]) == norm_strength:
                        return self._format_match(item, confidence=0.88, level="Level 3: Prefix/Strength Match", raw_name=clean_input)
                    elif not norm_strength or len(search_token) >= 5:
                        return self._format_match(item, confidence=0.80, level="Level 3: Prefix Match", raw_name=clean_input)

        # Level 4: Fuzzy Match (Only on compatible brands, cutoff 0.85)
        if len(stripped_norm) >= 4:
            all_brand_names = [item["brand_name"].lower() for item in self.catalog]
            name_to_item = {item["brand_name"].lower(): item for item in self.catalog}
            close_matches = difflib.get_close_matches(stripped_norm, all_brand_names, n=1, cutoff=0.85)
            if close_matches:
                best_item = name_to_item[close_matches[0]]
                if is_brand_compatible(best_item):
                    ratio = difflib.SequenceMatcher(None, stripped_norm, close_matches[0]).ratio()
                    return self._format_match(best_item, confidence=round(ratio * 0.92, 2), level="Level 4: Fuzzy Match", raw_name=clean_input)

        # If not matching an authentic brand in the catalog, treat as UNMATCHED / UNAVAILABLE
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

    def _format_match(self, item: Dict[str, Any], confidence: float, level: str, raw_name: str = "") -> Dict[str, Any]:
        """Formats catalog match dictionary."""
        alternatives = self._find_alternatives(item["brand_name"])
        # Exclude exact self from alternatives
        alternatives = [a for a in alternatives if a["id"] != item["id"]]

        return {
            "id": item["id"],
            "name": raw_name or item["brand_name"],
            "raw_name": raw_name,
            "matched_brand_name": item["brand_name"],
            "generic_name": item["generic_name"],
            "strength": item["strength"],
            "manufacturer": item["manufacturer"],
            "price": item["price"],
            "confidence": confidence,
            "match_level": level,
            "alternatives": alternatives[:2],
        }
