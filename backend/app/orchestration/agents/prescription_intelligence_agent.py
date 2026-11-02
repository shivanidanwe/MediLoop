"""
MediLoop Multi-Agent Orchestration Layer - Agent 2: Prescription Intelligence Agent.
Performs Medical Named Entity Recognition (NER) using Ollama in constrained JSON mode (format="json"),
matches medicines against the live database catalogue, calculates match confidence,
identifies ambiguities and missing strengths, and stores immutable extractions in prescription_extractions table.
"""
import re
import time
import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_, func

from app.models.medicine import Medicine
from app.models.orchestration import PrescriptionExtractionModel
from app.schemas.orchestration import (
    PrescriptionExtractionSchema,
    ExtractedMedicineSchema,
    CatalogueMatchSchema
)
from app.core.ollama_client import ollama_client

logger = logging.getLogger(__name__)


class PrescriptionIntelligenceAgent:
    """
    Agent 2: Prescription Intelligence Agent
    Parses OCR text into structured medical items using Ollama JSON mode and catalogue matching.
    """
    AGENT_ID = "prescription_intelligence_agent"
    VERSION = "2.0.0"

    def __init__(self, db: Session):
        self.db = db

    async def execute(
        self,
        prescription_id: int,
        patient_id: int,
        raw_text: str,
        ocr_confidence: float = 0.90,
        ocr_metadata: Optional[Dict[str, Any]] = None
    ) -> PrescriptionExtractionSchema:
        """
        Executes Medical NER on OCR text and matches items to catalogue.
        """
        start_time = time.perf_counter()

        if not raw_text or not raw_text.strip():
            # Return empty extraction structure
            empty_record = PrescriptionExtractionModel(
                prescription_id=prescription_id,
                patient_id=patient_id,
                extraction_status="FAILED",
                medicines_json=[],
                unrecognized_entities=["Empty prescription text"],
                missing_information=[],
                warnings=[],
                model_used="llama3.2:3b",
                published_to_patient=False
            )
            self.db.add(empty_record)
            self.db.commit()
            self.db.refresh(empty_record)
            duration_ms = (time.perf_counter() - start_time) * 1000.0
            return PrescriptionExtractionSchema(
                id=empty_record.id,
                prescription_id=prescription_id,
                patient_id=patient_id,
                extracted_medicines=[],
                unrecognized_medicines=["Empty prescription text"],
                ambiguous_medicines=[],
                missing_strength_medicines=[],
                total_medicines=0,
                matched_medicines_count=0,
                overall_confidence=0.0,
                extraction_notes="Prescription raw text was empty.",
                processing_time_ms=round(duration_ms, 2),
                created_at=empty_record.created_at
            )

        # Step 1: Medical NER via Ollama JSON Mode (format="json")
        raw_items: List[Dict[str, Any]] = []
        doctor_name = None
        clinic_name = None
        general_instructions = None

        system_prompt = (
            "You are a medical prescription Named Entity Recognition (NER) specialist. "
            "Extract all prescribed medicines into structured JSON format strictly obeying the schema."
        )
        prompt = (
            f"Extract structured prescription items from this exact prescription text:\n"
            f"```\n{raw_text}\n```\n"
            f"Return JSON strictly with the following keys:\n"
            f"- 'doctor_name' (str or null)\n"
            f"- 'clinic_name' (str or null)\n"
            f"- 'general_instructions' (str or null)\n"
            f"- 'medicines' (list of objects, where each object has:\n"
            f"    * 'medicine_name': exact medicine or brand name (e.g. 'Crocin', 'Amoxicillin', 'Dolo', 'Atorvastatin')\n"
            f"    * 'generic_name': pharmacologically active generic name if known (e.g. 'Paracetamol', 'Amoxicillin')\n"
            f"    * 'brand_name': brand name if known\n"
            f"    * 'strength': strength with units (e.g. '500mg', '650mg', '10mg', '400mg') or null if absent\n"
            f"    * 'dosage': dosage unit (e.g. '1 tablet', '1 capsule', '5ml')\n"
            f"    * 'frequency': dosage frequency (e.g. '1-0-1', 'Once daily', '1-1-1', 'Twice daily')\n"
            f"    * 'duration': duration of course (e.g. '5 days', '30 days', '7 days')\n"
            f"    * 'quantity': calculated quantity to dispense (integer or null, e.g. 10, 14, 30)\n"
            f"    * 'route': route of administration (e.g. 'Oral', 'Topical', 'Inhalation')\n"
            f"    * 'instructions': special instructions (e.g. 'Take after food', 'Before breakfast')\n"
            f"    * 'is_ambiguous': boolean, true if name or handwriting is unclear\n"
            f"    * 'confidence': float between 0.70 and 0.99\n"
            f")\n"
            f"If no medicines are prescribed, return 'medicines': []."
        )

        try:
            ner_res = await ollama_client.generate_json(prompt=prompt, system_prompt=system_prompt)
            if isinstance(ner_res, dict):
                doctor_name = ner_res.get("doctor_name")
                clinic_name = ner_res.get("clinic_name")
                general_instructions = ner_res.get("general_instructions")
                extracted_candidates = ner_res.get("medicines", [])
                if isinstance(extracted_candidates, list):
                    raw_items = extracted_candidates
        except Exception as e:
            logger.warning(f"Ollama JSON NER call failed or timed out: {e}")

        # Fallback Medical Regex Parser if Ollama returned nothing or failed
        if not raw_items:
            raw_items = self._regex_medical_parse(raw_text)

        # Step 2: Catalogue Matching & Normalization
        processed_medicines: List[ExtractedMedicineSchema] = []
        unrecognized_medicines: List[str] = []
        ambiguous_medicines: List[str] = []
        missing_strength_medicines: List[str] = []
        seen_names = set()

        for item in raw_items:
            name = str(item.get("medicine_name") or item.get("name") or "").strip()
            if not name or len(name) > 64:
                continue

            # Skip conversational junk
            if any(junk in name.lower() for junk in ["doctor", "clinic", "hospital", "date", "rx", "signature", "prescription"]):
                continue

            # Clean name (remove leading "Tab ", "Cap ", "Syp ")
            clean_name = re.sub(r'^(?:tab(?:let)?|cap(?:sule)?|syp(?:rup)?|inj(?:ection)?)\.?\s+', '', name, flags=re.IGNORECASE).strip()
            if not clean_name:
                continue

            strength = item.get("strength")
            if not strength:
                # Try to extract strength from clean_name if present (e.g. "Crocin 650mg")
                match_str = re.search(r'(\d+\s*(?:mg|ml|gm|mcg))', clean_name, re.IGNORECASE)
                if match_str:
                    strength = match_str.group(1).replace(" ", "")
                    clean_name = re.sub(r'\s*\d+\s*(?:mg|ml|gm|mcg)', '', clean_name, flags=re.IGNORECASE).strip()

            dedup_key = f"{clean_name.lower()}_{strength or ''}"
            if dedup_key in seen_names:
                continue
            seen_names.add(dedup_key)

            if not strength:
                missing_strength_medicines.append(clean_name)

            is_ambig = bool(item.get("is_ambiguous"))
            if is_ambig:
                ambiguous_medicines.append(clean_name)

            # Perform Catalogue Matching against DB
            catalogue_match = self._match_catalogue(clean_name, strength)
            if not catalogue_match:
                unrecognized_medicines.append(clean_name)

            # Calculate Quantity if missing
            calculated_qty = self._compute_quantity(
                raw_qty=item.get("quantity"),
                frequency=item.get("frequency") or "1-0-1",
                duration=item.get("duration") or "5 days"
            )

            med_conf = float(item.get("confidence") or ocr_confidence)
            med_conf = max(0.60, min(med_conf, 0.99))

            processed_medicines.append(ExtractedMedicineSchema(
                medicine_name=clean_name,
                generic_name=item.get("generic_name") or (catalogue_match.generic_name if catalogue_match else None),
                brand_name=item.get("brand_name") or (catalogue_match.brand_name if catalogue_match else clean_name),
                strength=strength,
                dosage=item.get("dosage") or "1 tablet",
                frequency=item.get("frequency") or "1-0-1",
                duration=item.get("duration") or "5 days",
                quantity=calculated_qty,
                route=item.get("route") or "Oral",
                instructions=item.get("instructions") or "Take after meals",
                confidence=round(med_conf, 2),
                is_ambiguous=is_ambig,
                catalogue_match=catalogue_match
            ))

        # Calculate Overall Metrics
        total_meds = len(processed_medicines)
        matched_count = sum(1 for m in processed_medicines if m.catalogue_match is not None)
        avg_conf = (
            sum(m.confidence for m in processed_medicines) / total_meds
            if total_meds > 0 else 0.0
        )

        # Step 3: Persist Extraction Record into Database (Immutable)
        extraction_record = PrescriptionExtractionModel(
            prescription_id=prescription_id,
            patient_id=patient_id,
            extraction_status="SUCCESS" if total_meds > 0 else "FAILED",
            medicines_json=[m.model_dump() for m in processed_medicines],
            unrecognized_entities=unrecognized_medicines,
            missing_information=missing_strength_medicines,
            warnings=ambiguous_medicines,
            model_used="llama3.2:3b",
            published_to_patient=True
        )
        self.db.add(extraction_record)
        self.db.commit()
        self.db.refresh(extraction_record)

        duration_ms = (time.perf_counter() - start_time) * 1000.0

        return PrescriptionExtractionSchema(
            id=extraction_record.id,
            prescription_id=prescription_id,
            patient_id=patient_id,
            extracted_medicines=processed_medicines,
            unrecognized_medicines=unrecognized_medicines,
            ambiguous_medicines=ambiguous_medicines,
            missing_strength_medicines=missing_strength_medicines,
            doctor_name=doctor_name,
            clinic_name=clinic_name,
            general_instructions=general_instructions,
            total_medicines=total_meds,
            matched_medicines_count=matched_count,
            overall_confidence=round(avg_conf, 2),
            extraction_notes=f"Successfully extracted {total_meds} medicines. {matched_count}/{total_meds} matched to catalogue.",
            processing_time_ms=round(duration_ms, 2),
            created_at=extraction_record.created_at
        )

    def _match_catalogue(self, name: str, strength: Optional[str]) -> Optional[CatalogueMatchSchema]:
        """
        Matches a prescribed medicine name and optional strength against the medicine catalogue.
        """
        if not name:
            return None

        # Clean search term
        term = name.strip().lower()

        # 1. Exact or ILIKE match on brand_name or generic_name
        query = self.db.query(Medicine).filter(
            or_(
                func.lower(Medicine.brand_name) == term,
                func.lower(Medicine.generic_name) == term,
                Medicine.brand_name.ilike(f"%{term}%"),
                Medicine.generic_name.ilike(f"%{term}%")
            )
        )
        candidates = query.all()

        if not candidates:
            # Try matching individual significant tokens
            tokens = [t for t in term.split() if len(t) > 3]
            for tok in tokens:
                candidates = self.db.query(Medicine).filter(
                    or_(
                        Medicine.brand_name.ilike(f"%{tok}%"),
                        Medicine.generic_name.ilike(f"%{tok}%")
                    )
                ).all()
                if candidates:
                    break

        if not candidates:
            return None

        # Pick best candidate based on strength match
        best_cand = candidates[0]
        match_score = 0.85

        if strength:
            clean_str = strength.lower().replace(" ", "")
            for c in candidates:
                c_str = (c.strength or "").lower().replace(" ", "")
                if c_str and clean_str in c_str:
                    best_cand = c
                    match_score = 0.98
                    break

        return CatalogueMatchSchema(
            medicine_id=best_cand.id,
            brand_name=best_cand.brand_name,
            generic_name=best_cand.generic_name,
            strength=best_cand.strength,
            dosage_form=best_cand.dosage_form or "Tablet",
            unit_price=float(getattr(best_cand, "price", 35.0) or 35.0),
            match_confidence=match_score
        )

    def _compute_quantity(self, raw_qty: Any, frequency: str, duration: str) -> int:
        """Computes quantity based on daily dosage frequency and duration if not explicit."""
        if raw_qty is not None:
            try:
                val = int(raw_qty)
                if val > 0:
                    return val
            except (ValueError, TypeError):
                pass

        # Parse frequency: count doses per day
        daily_doses = 2  # default 1-0-1
        freq_lower = frequency.lower()
        if "1-1-1" in freq_lower or "tid" in freq_lower or "three" in freq_lower:
            daily_doses = 3
        elif "1-0-1" in freq_lower or "bid" in freq_lower or "twice" in freq_lower:
            daily_doses = 2
        elif "0-0-1" in freq_lower or "1-0-0" in freq_lower or "od" in freq_lower or "once" in freq_lower:
            daily_doses = 1
        elif "1-1-1-1" in freq_lower or "qid" in freq_lower:
            daily_doses = 4

        # Parse duration: days
        days = 5
        dur_match = re.search(r'(\d+)', duration)
        if dur_match:
            days = int(dur_match.group(1))

        return daily_doses * days

    def _regex_medical_parse(self, raw_text: str) -> List[Dict[str, Any]]:
        """Fallback regex-based medical parsing if Ollama is unreachable."""
        items = []
        lines = [l.strip() for l in raw_text.splitlines() if l.strip()]

        known_patterns = [
            r'(?:tab|cap|syp|inj)?\.?\s*([A-Za-z]{3,25})\s*(\d+\s*(?:mg|ml|gm))?',
        ]

        for line in lines:
            if re.match(r'^(?:rx|dr\.|clinic|hospital|patient|date)', line, re.IGNORECASE):
                continue
            for pat in known_patterns:
                m = re.search(pat, line, re.IGNORECASE)
                if m:
                    med_name = m.group(1).strip()
                    strength = m.group(2).strip() if m.group(2) else None
                    if len(med_name) >= 3 and med_name.lower() not in ["tab", "cap", "syp", "inj", "days", "food"]:
                        items.append({
                            "medicine_name": med_name.capitalize(),
                            "strength": strength,
                            "dosage": "1 tablet",
                            "frequency": "1-0-1",
                            "duration": "5 days",
                            "quantity": 10,
                            "route": "Oral",
                            "instructions": "Take after meals",
                            "is_ambiguous": False,
                            "confidence": 0.82
                        })
                        break
        return items
