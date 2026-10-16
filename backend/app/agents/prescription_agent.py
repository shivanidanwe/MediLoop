"""
MediLoop Prescription Intelligence Agent.
Extracts structured medicine details and confidence metrics from OCR output.
"""
import re
from typing import Any, Dict, List, Tuple
from app.agents.base_agent import BaseAgent
from app.agents.context import AgentContext
from app.agents.events import AgentEvent
from app.agents.exceptions import AgentValidationError


class PrescriptionIntelligenceAgent(BaseAgent):
    """
    Agent responsible for parsing raw OCR prescription text into structured
    medical records containing medicine name, strength, dosage, frequency,
    duration, quantity, and confidence scores.
    """

    @property
    def name(self) -> str:
        return "prescription_intelligence_agent"

    @property
    def description(self) -> str:
        return (
            "Extracts structured medicine details (name, strength, dosage, "
            "frequency, duration, quantity) and confidence scores from OCR text."
        )

    @property
    def handled_events(self) -> List[AgentEvent]:
        return [AgentEvent.OCR_COMPLETED, AgentEvent.PRESCRIPTION_UPLOADED]

    async def can_handle(self, event: AgentEvent, context: AgentContext) -> bool:
        """
        Agent handles OCR_COMPLETED or PRESCRIPTION_UPLOADED events.
        """
        return event in self.handled_events

    async def validate(self, context: AgentContext) -> bool:
        """
        Validates that OCR text exists in shared context prior to execution.
        """
        if not context.ocr_text or not context.ocr_text.strip():
            raise AgentValidationError(
                "PrescriptionIntelligenceAgent validation failed: 'ocr_text' is missing or empty."
            )
        return True

    async def execute(self, context: AgentContext) -> AgentContext:
        """
        Parses context.ocr_text via Ollama JSON Medical NER with regex fallback.
        """
        raw_text = context.ocr_text or ""
        lines = [line.strip() for line in raw_text.splitlines() if line.strip()]

        extracted_list: List[Dict[str, Any]] = []
        confidences: List[float] = []

        # 1. Try Ollama JSON Medical NER first
        try:
            from app.core.ollama_client import ollama_client
            prompt = (
                f"You are a Clinical Pharmacist NER system. Extract all prescribed medicines from this text:\n"
                f"```\n{raw_text}\n```\n"
                f"Return JSON strictly with the key 'medicines', where each object has: "
                f"'name' (str), 'strength' (str), 'dosage' (str), 'frequency' (str), 'duration' (str), 'quantity' (int or str), 'confidence' (float between 0.8 and 1.0)."
            )
            ner_res = await ollama_client.generate_json(
                prompt=prompt,
                system_prompt="You are a clinical pharmacy entity extractor. Output valid JSON only."
            )
            ai_meds = ner_res.get("medicines", [])
            if isinstance(ai_meds, list) and len(ai_meds) > 0:
                for m in ai_meds:
                    if m.get("name"):
                        conf = float(m.get("confidence") or 0.92)
                        extracted_list.append({
                            "name": str(m.get("name")),
                            "strength": str(m.get("strength") or ""),
                            "dosage": str(m.get("dosage") or "1 tab"),
                            "frequency": str(m.get("frequency") or "Once daily"),
                            "duration": str(m.get("duration") or "5 days"),
                            "quantity": str(m.get("quantity") or "10"),
                            "confidence": min(conf, 0.98),
                        })
                        confidences.append(conf)
        except Exception:
            pass

        # 2. If Ollama was offline or returned nothing, fall back to medical regex parsing
        if not extracted_list:
            # Common non-medicine header/footer keywords
            header_noise_keywords = [
                'dr.', 'doctor', 'm.d.', 'mbbs', 'dnb', 'clinic', 'hospital',
                'prescription', 'rx prescription', 'patient', 'date:', 'age:', 'gender:',
                'reg. no', 'signature', 'cardiology', 'neurology', 'orthopedics'
            ]

            for line in lines:
                line_lower = line.lower()
                if any(kw in line_lower for kw in header_noise_keywords):
                    # Only skip if line has no medical strength or frequency
                    has_medical_data = bool(
                        re.search(r'\b\d+\s*(?:mg|g|mcg|ml|iu|%)\b', line_lower) or
                        re.search(r'\b[01]\-[01]\-[01]\b', line_lower)
                    )
                    if not has_medical_data:
                        continue

                parsed_item, conf = self._parse_medicine_line(line)
                if parsed_item and parsed_item["name"]:
                    extracted_list.append(parsed_item)
                    confidences.append(conf)
                    if conf < 0.70:
                        context.add_warning(
                            f"Low extraction confidence ({conf:.2f}) for medicine '{parsed_item['name']}' in line: '{line}'"
                        )

        if not extracted_list:
            context.add_warning("Prescription Intelligence Agent found no valid medicine entries in OCR text.")

        avg_confidence = round(sum(confidences) / len(confidences), 2) if confidences else 0.0

        context.extracted_medicines = extracted_list
        context.metadata["prescription_intelligence"] = {
            "total_medicines_extracted": len(extracted_list),
            "average_confidence": avg_confidence,
            "parsing_status": "SUCCESS" if extracted_list else "NO_MEDICINES_FOUND",
        }

        return context

    def _parse_medicine_line(self, line: str) -> Tuple[Dict[str, Any], float]:
        """
        Parses a single line of prescription text using medical regex patterns.
        """
        working_line = line

        # Strip leading numbers/bullets/Rx like 'Rx:', 'Rx ', '1.', '2)', '1 -', '#1'
        working_line = re.sub(r'^(?:rx:?\s*|\d+[\.\)\-]?|#\d+)\s*', '', working_line, flags=re.IGNORECASE).strip()

        # 1. Extract Strength (e.g. 500mg, 250 mg, 10ml, 50mcg)
        strength_match = re.search(r'\b(\d+(?:\.\d+)?\s*(?:mg|g|mcg|ml|iu|%))\b', working_line, re.IGNORECASE)
        strength = strength_match.group(1) if strength_match else ""
        if strength_match:
            working_line = working_line.replace(strength_match.group(0), " ")

        # 2. Extract Duration (e.g. for 5 days, 1 week, 10d, 5 days)
        duration_match = re.search(r'\b(?:for\s*)?(\d+\s*(?:days?|weeks?|months?|d|w|m))\b', working_line, re.IGNORECASE)
        duration = duration_match.group(1) if duration_match else ""
        if duration_match:
            working_line = working_line.replace(duration_match.group(0), " ")

        # 3. Extract Frequency (e.g. 1-0-1, BID, once daily, twice a day, after meals)
        freq_patterns = [
            r'\b([01]\-[01]\-[01](?:\-[01])?)\b',
            r'\b(once daily|twice daily|thrice daily|four times daily|once a day|twice a day|three times a day|as needed)\b',
            r'\b(OD|BID|TID|QID|HS|PRN|STAT|BD)\b',
            r'\b(every \d+\s*(?:hours|hrs))\b',
        ]
        frequency = ""
        for pattern in freq_patterns:
            f_match = re.search(pattern, working_line, re.IGNORECASE)
            if f_match:
                frequency = f_match.group(1)
                working_line = working_line.replace(f_match.group(0), " ")
                break

        # 4. Extract Dosage (e.g. 1 tab, 2 capsules, 5 ml, 1 puff)
        dosage_match = re.search(r'\b(\d+\s*(?:tablets?|tabs?|capsules?|caps?|puffs?|drops?|pills?))\b', working_line, re.IGNORECASE)
        dosage = dosage_match.group(1) if dosage_match else ""
        if dosage_match:
            working_line = working_line.replace(dosage_match.group(0), " ")

        # 5. Extract Quantity (e.g. Qty: 10, Qty 30, x30)
        qty_match = re.search(r'\b(?:qty:?\s*|x)(\d+)\b', working_line, re.IGNORECASE)
        quantity = qty_match.group(1) if qty_match else ""
        if qty_match:
            working_line = working_line.replace(qty_match.group(0), " ")

        # 6. Extract Medicine Name (Clean remaining words)
        cleaned_name = re.sub(r'[\-\:]+$', '', working_line).strip()
        cleaned_name = re.sub(r'^[^\w]+|[^\w]+$', '', cleaned_name).strip()
        cleaned_name = re.sub(r'\s+', ' ', cleaned_name)

        if not cleaned_name or len(cleaned_name) < 2:
            return {}, 0.0

        # Calculate Confidence Score
        confidence = 0.50
        if len(cleaned_name) >= 3:
            confidence += 0.20
        if strength or dosage:
            confidence += 0.15
        if frequency:
            confidence += 0.10
        if duration or quantity:
            confidence += 0.03

        confidence = min(round(confidence, 2), 0.98)

        structured_item = {
            "name": cleaned_name,
            "strength": strength,
            "dosage": dosage,
            "frequency": frequency,
            "duration": duration,
            "quantity": quantity,
            "confidence": confidence,
        }

        return structured_item, confidence
