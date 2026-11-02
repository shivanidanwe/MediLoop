"""
MediLoop Prescription Intelligence Agent.
Extracts structured medicine details and clinical entities from OCR output adhering
strictly to the MediLoop Exact Prescription Extraction Display Format.
"""
import re
from typing import Any, Dict, List, Optional, Tuple
from app.agents.base_agent import BaseAgent
from app.agents.context import AgentContext
from app.agents.events import AgentEvent
from app.agents.exceptions import AgentValidationError


def format_exact_prescription_display(
    entities: Dict[str, Optional[str]],
    medicines: List[Dict[str, Any]]
) -> str:
    """
    Formats extracted prescription details strictly adhering to MediLoop
    Exact Prescription Extraction Display Format specification.

    REQUIRED OUTPUT FORMAT:
    **Prescription Details:**

    Hospital / Clinic: [Extracted hospital or clinic name]

    Prescribing Doctor: [Doctor name and designation/specialization, if available]

    Patient Name: [Extracted patient name]

    Age / Gender: [Extracted age / gender]

    Patient Address: [Extracted address]

    Known Allergies: [Extracted allergies, if explicitly documented]

    Diagnosis: [Extracted diagnosis, if explicitly documented]

    Clinical Vitals: [Extracted BP, pulse, temperature, SpO2, weight and other available vitals]

    **Prescribed Medicines:**

    1. [Medicine Name] | Strength: [Strength] | Dosage: [Dosage] | Frequency: [Frequency] | Duration: [Duration] | Qty: [Quantity]

    **Medical Advice & Instructions:**

    [Extract all additional doctor messages, precautions, dietary advice, follow-up instructions, investigation recommendations, referrals and other written instructions.]
    """
    MISSING_TEXT = "Not mentioned in prescription."
    UNREADABLE_TEXT = "Unable to read clearly."

    def clean_val(val: Any) -> str:
        if val is None:
            return MISSING_TEXT
        v = str(val).strip()
        if not v:
            return MISSING_TEXT
        if any(un in v.lower() for un in ["unable to read", "unreadable", "blurry", "too small", "cannot read"]):
            return UNREADABLE_TEXT
        if v.lower() in ["not mentioned in prescription.", "not mentioned", "none", "n/a", "null", "nil"]:
            return MISSING_TEXT
        return v

    hospital = clean_val(entities.get("hospital"))
    doctor = clean_val(entities.get("doctor"))
    patient_name = clean_val(entities.get("patient_name"))
    age_gender = clean_val(entities.get("age_gender"))
    address = clean_val(entities.get("address"))
    allergies = clean_val(entities.get("allergies"))
    diagnosis = clean_val(entities.get("diagnosis"))
    vitals = clean_val(entities.get("vitals"))
    advice = clean_val(entities.get("advice"))

    sections: List[str] = [
        "**Prescription Details:**",
        "",
        f"Hospital / Clinic: {hospital}",
        "",
        f"Prescribing Doctor: {doctor}",
        "",
        f"Patient Name: {patient_name}",
        "",
        f"Age / Gender: {age_gender}",
        "",
        f"Patient Address: {address}",
        "",
        f"Known Allergies: {allergies}",
        "",
        f"Diagnosis: {diagnosis}",
        "",
        f"Clinical Vitals: {vitals}",
        "",
        "**Prescribed Medicines:**",
        "",
    ]

    if medicines and len(medicines) > 0:
        for idx, m in enumerate(medicines, 1):
            raw_name = clean_val(m.get("name") or m.get("medicine_name"))
            if raw_name == MISSING_TEXT:
                raw_name = UNREADABLE_TEXT

            is_uncertain = bool(m.get("is_ambiguous")) or (float(m.get("confidence") or 1.0) < 0.75)
            if is_uncertain and "needs verification" not in raw_name.lower():
                name_display = f"{raw_name} (Needs verification)"
            else:
                name_display = raw_name

            strength_display = clean_val(m.get("strength"))
            dosage_display = clean_val(m.get("dosage"))
            freq_display = clean_val(m.get("frequency"))

            dur = m.get("duration") or m.get("duration_days")
            dur_str = str(dur).strip() if dur is not None else ""
            if dur_str.isdigit():
                dur_str = f"{dur_str} days"
            dur_display = clean_val(dur_str)

            qty = m.get("quantity") or m.get("calculated_quantity")
            qty_display = clean_val(qty)

            med_line = (
                f"{idx}. {name_display} | "
                f"Strength: {strength_display} | "
                f"Dosage: {dosage_display} | "
                f"Frequency: {freq_display} | "
                f"Duration: {dur_display} | "
                f"Qty: {qty_display}"
            )
            sections.append(med_line)
            sections.append("")
    else:
        sections.append(f"1. {UNREADABLE_TEXT} (Needs verification) | Strength: {MISSING_TEXT} | Dosage: {MISSING_TEXT} | Frequency: {MISSING_TEXT} | Duration: {MISSING_TEXT} | Qty: {MISSING_TEXT}")
        sections.append("")

    sections.append("**Medical Advice & Instructions:**")
    sections.append("")
    sections.append(f"{advice}")

    return "\n".join(sections).strip()


class PrescriptionIntelligenceAgent(BaseAgent):
    """
    Agent responsible for parsing raw OCR prescription text into structured
    medical records containing medicine name, strength, dosage, frequency,
    duration, quantity, and clinical metadata strictly following MediLoop format rules.
    """

    @property
    def name(self) -> str:
        return "prescription_intelligence_agent"

    @property
    def description(self) -> str:
        return (
            "Extracts structured medicine details (name, strength, dosage, "
            "frequency, duration, quantity) and clinical entities from OCR text."
        )

    @property
    def handled_events(self) -> List[AgentEvent]:
        return [AgentEvent.OCR_COMPLETED, AgentEvent.PRESCRIPTION_UPLOADED]

    async def can_handle(self, event: AgentEvent, context: AgentContext) -> bool:
        return event in self.handled_events

    async def validate(self, context: AgentContext) -> bool:
        if not context.ocr_text or not context.ocr_text.strip():
            raise AgentValidationError(
                "PrescriptionIntelligenceAgent validation failed: 'ocr_text' is missing or empty."
            )
        return True

    async def execute(self, context: AgentContext) -> AgentContext:
        """
        Parses context.ocr_text via Ollama JSON Medical NER with regex fallback.
        Generates structured summary in exact required display format.
        """
        raw_text = context.ocr_text or ""
        lines = [line.strip() for line in raw_text.splitlines() if line.strip()]

        if not lines:
            empty_entities = {}
            empty_summary = format_exact_prescription_display(empty_entities, [])
            context.extracted_medicines = []
            context.metadata["prescription_intelligence"] = {
                "total_medicines_extracted": 0,
                "average_confidence": 0.0,
                "parsing_status": "NO_MEDICINES_FOUND",
                "doctor": "Not mentioned in prescription.",
                "patient": "Not mentioned in prescription.",
                "hospital": "Not mentioned in prescription.",
                "address": "Not mentioned in prescription.",
                "allergies": "Not mentioned in prescription.",
                "diagnosis": "Not mentioned in prescription.",
                "vitals": "Not mentioned in prescription.",
                "instructions": "Not mentioned in prescription.",
                "clinical_entities": empty_entities,
                "structured_summary": empty_summary,
            }
            return context

        extracted_list: List[Dict[str, Any]] = []
        confidences: List[float] = []
        seen_med_keys = set()
        ai_entities: Dict[str, Optional[str]] = {}

        # 1. Try Ollama JSON Medical NER first for clinical entities & medicines
        try:
            from app.core.ollama_client import ollama_client
            system_prompt = (
                "You are an expert clinical prescription parser. "
                "Extract all clinical details and prescribed medicines strictly from the provided prescription text. "
                "Never fabricate or guess details. If a field is not present or unreadable, set it to null."
            )
            prompt = (
                f"Extract structured prescription data from this exact text:\n"
                f"```\n{raw_text}\n```\n"
                f"Return JSON strictly with the following schema:\n"
                f"{{\n"
                f'  "hospital": str or null,\n'
                f'  "doctor": str or null (name and designation if available),\n'
                f'  "patient_name": str or null,\n'
                f'  "age_gender": str or null (e.g. "28 Years / Male"),\n'
                f'  "address": str or null,\n'
                f'  "allergies": str or null (e.g. "Dust, Pollen"),\n'
                f'  "diagnosis": str or null,\n'
                f'  "vitals": str or null (e.g. "BP: 118/74 mmHg | PR: 82/min | SpO2: 98%"),\n'
                f'  "advice": str or null,\n'
                f'  "medicines": [\n'
                f"    {{\n"
                f'      "name": str (exact brand or generic name written),\n'
                f'      "strength": str or null (e.g. "160mcg", "5mg", "500mg"),\n'
                f'      "form": str or null ("Tablet", "Inhaler", "Capsule"),\n'
                f'      "dosage": str or null (e.g. "2 puffs", "1 tab"),\n'
                f'      "frequency": str or null (e.g. "twice daily (morning & night)", "1-0-1", "night"),\n'
                f'      "duration": str or null (e.g. "6 weeks", "7 days"),\n'
                f'      "quantity": str or null (e.g. "10", "1"),\n'
                f'      "raw_evidence_text": str,\n'
                f'      "is_ambiguous": bool,\n'
                f'      "confidence": float\n'
                f"    }}\n"
                f"  ]\n"
                f"}}"
            )
            ner_res = await ollama_client.generate_json(
                prompt=prompt,
                system_prompt=system_prompt
            )
            if isinstance(ner_res, dict):
                for k in ["hospital", "doctor", "patient_name", "age_gender", "address", "allergies", "diagnosis", "vitals", "advice"]:
                    val = ner_res.get(k)
                    if val and str(val).strip() and str(val).lower() not in ["null", "none", "n/a"]:
                        ai_entities[k] = str(val).strip()

                ai_meds = ner_res.get("medicines", [])
                if isinstance(ai_meds, list) and len(ai_meds) > 0:
                    for m in ai_meds:
                        m_name = str(m.get("name") or "").strip()
                        if not m_name or len(m_name) > 40 or len(m_name.split()) > 5:
                            continue
                        if any(marker in m_name.lower() for marker in ["blurry", "unreadable", "transcription", "language model", "sorry"]):
                            continue
                        m_str = str(m.get("strength") or "").strip() or None
                        dedup_key = f"{m_name.lower()}_{m_str or ''}"
                        if dedup_key in seen_med_keys:
                            continue
                        seen_med_keys.add(dedup_key)

                        conf = float(m.get("confidence") or 0.92)
                        is_ambig = bool(m.get("is_ambiguous")) or conf < 0.75 or not m_str
                        extracted_list.append({
                            "name": m_name,
                            "strength": m_str,
                            "form": str(m.get("form") or "") if m.get("form") else None,
                            "dosage": str(m.get("dosage") or "") if m.get("dosage") else None,
                            "frequency": str(m.get("frequency") or "") if m.get("frequency") else None,
                            "duration": str(m.get("duration") or "") if m.get("duration") else None,
                            "quantity": str(m.get("quantity") or "") if m.get("quantity") else None,
                            "raw_evidence_text": str(m.get("raw_evidence_text") or m_name),
                            "is_ambiguous": is_ambig,
                            "requires_review": is_ambig,
                            "confidence": min(conf, 0.98),
                        })
                        confidences.append(conf)
        except Exception:
            pass

        # 2. Extract clinical entities via rigorous regex (merge with any AI entities found)
        regex_entities = self._extract_clinical_entities(raw_text)
        final_entities: Dict[str, Optional[str]] = {}
        for k in ["hospital", "doctor", "patient_name", "age_gender", "address", "allergies", "diagnosis", "vitals", "advice"]:
            final_entities[k] = ai_entities.get(k) or regex_entities.get(k)

        # 3. If Ollama was offline or returned no medicines, fall back to medical regex parsing
        if not extracted_list:
            header_noise_keywords = [
                'dr.', 'doctor', 'm.d.', 'mbbs', 'dnb', 'clinic', 'hospital',
                'prescription', 'rx prescription', 'patient', 'date:', 'age:', 'gender:',
                'reg. no', 'signature', 'cardiology', 'neurology', 'orthopedics',
                'chemist:', 'chemist', 'medical store', 'kothrud', 'baner'
            ]

            for line in lines:
                line_lower = line.lower()
                if any(kw in line_lower for kw in header_noise_keywords):
                    has_medical_data = bool(
                        re.search(r'\b\d+\s*(?:mg|g|mcg|ml|iu|%)\b', line_lower) or
                        re.search(r'\b[01]\-[01]\-[01]\b', line_lower)
                    )
                    if not has_medical_data:
                        continue

                parsed_item, conf = self._parse_medicine_line(line)
                if parsed_item and parsed_item.get("name"):
                    extracted_list.append(parsed_item)
                    confidences.append(conf)

        if not extracted_list:
            context.add_warning("Prescription Intelligence Agent found no valid medicine entries in OCR text.")

        avg_confidence = round(sum(confidences) / len(confidences), 2) if confidences else 0.0

        # Build exact display format report
        structured_summary = format_exact_prescription_display(final_entities, extracted_list)

        context.extracted_medicines = extracted_list
        context.metadata["prescription_intelligence"] = {
            "total_medicines_extracted": len(extracted_list),
            "average_confidence": avg_confidence,
            "parsing_status": "SUCCESS" if extracted_list else "NO_MEDICINES_FOUND",
            "doctor": final_entities.get("doctor") or "Not mentioned in prescription.",
            "patient": final_entities.get("patient_name") or "Not mentioned in prescription.",
            "hospital": final_entities.get("hospital") or "Not mentioned in prescription.",
            "address": final_entities.get("address") or "Not mentioned in prescription.",
            "allergies": final_entities.get("allergies") or "Not mentioned in prescription.",
            "diagnosis": final_entities.get("diagnosis") or "Not mentioned in prescription.",
            "vitals": final_entities.get("vitals") or "Not mentioned in prescription.",
            "instructions": final_entities.get("advice") or "Not mentioned in prescription.",
            "clinical_entities": final_entities,
            "structured_summary": structured_summary,
        }

        return context

    def _extract_clinical_entities(self, raw_text: str) -> Dict[str, Optional[str]]:
        """
        Extracts structured clinical metadata from raw prescription text.
        Adheres strictly to extraction rules:
        - Never invents patient names, doctor names, addresses, allergies, diagnosis, or vitals.
        - Missing fields evaluate to None (rendered as 'Not mentioned in prescription.').
        - Unreadable fields evaluate to 'Unable to read clearly.'.
        """
        clean_text = raw_text.replace('\r', ' ')

        # 1. Hospital / Clinic
        hospital = None
        hosp_match = re.search(
            r'([A-Za-z0-9\s\.\,\-\&]{3,60}?(?:Multi[\-\s]?Speciality|General|Super[\-\s]?Speciality|City|District|Care|Sunrise|Sevashree|Memorial|Apollo|Max|Fortis|AIIMS)\s*(?:Hospital|Clinic|Medical\s*Centre|Healthcare))',
            clean_text, re.IGNORECASE
        )
        if hosp_match:
            h = hosp_match.group(1).strip()
            h = re.sub(r'^(?:Doctor\s*\/\s*Clinic\s*:\s*|Patient\s*Name\s*|Advice\s*:\s*|Vitals\s*:\s*|\d+\.\s*|\:\s*)+', '', h, flags=re.IGNORECASE).strip()
            if len(h) >= 4 and not any(kw in h.lower() for kw in ["patient", "vitals", "allergies", "doctor / clinic"]):
                hospital = h
        if not hospital:
            h2 = re.search(r'([A-Za-z0-9\s\.\-]{3,45}\s*(?:Hospital|Clinic|Medical\s*Centre|Healthcare))', clean_text, re.IGNORECASE)
            if h2:
                h = h2.group(1).strip()
                h = re.sub(r'^(?:Doctor\s*\/\s*Clinic\s*:\s*|Patient\s*Name\s*|\:\s*)+', '', h, flags=re.IGNORECASE).strip()
                if len(h) >= 4 and not any(kw in h.lower() for kw in ["patient", "doctor", "vitals", "allergies"]):
                    hospital = h

        # 2. Prescribing Doctor & Designation
        doctor_str = None
        doc_match = re.search(
            r'\b(?:Prescribing\s*Doctor|Doctor)\b\s*[:\s\-]*Dr\.?\s+([A-Za-z\.\s]{2,35}?)(?:\s*\(|\s*Consultant|\s*Pulmonology|\s*Physician|\s*MBBS|\s*MD|\n|\r|$)',
            clean_text, re.IGNORECASE
        )
        if not doc_match:
            doc_match = re.search(r'\b(?:Dr\.?|Doctor)\s+([A-Za-z\.\s]{2,30}?)(?:\s*\(|\s*Consultant|\s*Pulmonology|\s*Physician|\s*MBBS|\s*MD|\n|\r|$)', clean_text, re.IGNORECASE)

        if doc_match:
            doc_name = doc_match.group(1).strip()
            doc_name = re.sub(r'^(?:Dr\.?|Doctor)\s+', '', doc_name, flags=re.IGNORECASE).strip()
            doc_name = re.sub(r'[\.\s\(\)]+$', '', doc_name)
            if len(doc_name) >= 2 and not any(kw in doc_name.lower() for kw in ["patient", "hospital", "clinic", "date", "sevashree"]):
                dept_match = re.search(
                    r'(?:Consultant\s*[\-\:]\s*([A-Za-z\s]+?)|Department of\s+([A-Za-z\s]+?)|(MBBS[A-Za-z\s\,\.]*|MD[A-Za-z\s\,\.]*|M\.D\.[A-Za-z\s\,\.]*|Pulmonologist|Physician|Cardiologist))(?:Patient|Date|\d|\n|\r|Dr|Reg|$|\))',
                    clean_text, re.IGNORECASE
                )
                dept = ""
                if dept_match:
                    dept = (dept_match.group(1) or dept_match.group(2) or dept_match.group(3) or "").strip()
                    dept = re.sub(r'[\s\)]+', ' ', dept).strip()
                if dept:
                    doctor_str = f"Dr. {doc_name} ({dept})"
                else:
                    doctor_str = f"Dr. {doc_name}"

        # 3. Patient Name
        patient_name = None
        pt_match = re.search(
            r'(?:Patient\s*Name|Patient|Pt\.?\s*Name)\s*[:\s\-]*([A-Za-z\s\.]{2,30}?)(?=(?:Age|\d{1,3}\s*Years?|\d{1,3}\s*Yrs?|Sex|Gender|URID|UID|Address|Diagnosis|Date|Mobile|Phone|MRN|Ref|Rx|$|\n|\r))',
            clean_text, re.IGNORECASE
        )
        if pt_match:
            p_cand = pt_match.group(1).strip()
            p_cand = re.sub(r'^(?:Age\s*\/|Sex\s*|URID|UID|Address|Mr\.?|Mrs\.?|Ms\.?)+', '', p_cand).strip()
            if len(p_cand) >= 2 and not any(kw in p_cand.lower() for kw in ["patient", "doctor", "clinic", "hospital", "date", "consultant"]):
                patient_name = p_cand

        # 4. Age / Gender
        age_gender = None
        age_val = None
        gender_val = None
        age_match = re.search(r'\b(\d{1,3})\s*(?:Years?|Yrs?|Y\/o|Y)\b', clean_text, re.IGNORECASE)
        if age_match:
            age_val = f"{age_match.group(1)} Years"
        gender_match = re.search(r'\b(Male|Female|Other)\b', clean_text, re.IGNORECASE)
        if not gender_match:
            g_short = re.search(r'(?:Sex|Gender)\s*[:\s\-]*\s*([MF])\b', clean_text, re.IGNORECASE)
            if g_short:
                gender_val = "Male" if g_short.group(1).upper() == "M" else "Female"
        else:
            gender_val = gender_match.group(1).capitalize()

        if age_val and gender_val:
            age_gender = f"{age_val} / {gender_val}"
        elif age_val:
            age_gender = f"{age_val} / Not mentioned in prescription."
        elif gender_val:
            age_gender = f"Not mentioned in prescription. / {gender_val}"

        # 5. Patient Address
        address = None
        addr_match = re.search(
            r'(?:Patient\s*Address|Address|Addr)\s*[:\s\-]*([^\n\r]+?)(?=(?:Phone|Mobile|Contact|Date|Allergies|Diagnosis|Vitals|Rx|Pin|Reg|$))',
            clean_text, re.IGNORECASE
        )
        if addr_match:
            a_cand = addr_match.group(1).strip()
            a_cand = re.sub(r'(?:Prescribing\s*Doctor|Doctor|Hospital|Diagnosis|Allergies).*', '', a_cand, flags=re.IGNORECASE).strip()
            a_cand = re.sub(r'\(as per history\)', '', a_cand, flags=re.IGNORECASE).strip()
            if len(a_cand) >= 4 and not any(kw in a_cand.lower() for kw in ["diagnosis", "allergies", "doctor", "hospital"]):
                address = a_cand
        if not address:
            city_match = re.search(r'\b((?:Baner|Kothrud|Viman Nagar|Hinjawadi|Hadapsar|Shivaji Nagar|Andheri|Bandra)[,\s]+[A-Za-z\s]+)', clean_text, re.IGNORECASE)
            if city_match:
                address = city_match.group(1).strip()

        # 6. Known Allergies
        allergies = None
        allergy_match = re.search(
            r'\b(?:Known\s*Allergies|Allergies|Allergy)\b\s*[:\s\-]*([^\n\r]+)',
            clean_text, re.IGNORECASE
        )
        if allergy_match:
            al_cand = allergy_match.group(1).strip()
            al_cand = re.sub(r'^(?:as per history\s*[:\)]*|history\s*[:\)]*|,\s*)', '', al_cand, flags=re.IGNORECASE).strip()
            al_cand = re.sub(r'(?:Diagnosis|Co-morbidities|Vitals|BP).*', '', al_cand, flags=re.IGNORECASE).strip()
            if len(al_cand) >= 2 and not any(kw in al_cand.lower() for kw in ["diagnosis", "co-morbidities", "vitals", "none", "nil", "n/a"]):
                allergies = al_cand

        # 7. Diagnosis
        diagnosis = None
        diag_match = re.search(
            r'\b(?:Diagnosis|Impression|Assessment|Dx)\b\s*[:\s\-]*([^\n\r]+)',
            clean_text, re.IGNORECASE
        )
        if diag_match:
            dg_cand = diag_match.group(1).strip()
            if len(dg_cand) >= 3 and not any(kw in dg_cand.lower() for kw in ["co-morbidities", "vitals", "prescription", "advice"]):
                diagnosis = dg_cand

        # 8. Clinical Vitals
        vitals = None
        vitals_match = re.search(
            r'\b(?:Vitals|Clinical\s*Vitals)\b\s*[:\s\-]*([^\n\r]+)',
            clean_text, re.IGNORECASE
        )
        if not vitals_match:
            vitals_match = re.search(
                r'((?:BP|Blood\s*Pressure|PR|Pulse|Pulse\s*Rate|Heart\s*Rate|SpO2|sp02|Temp|Temperature|Weight|Wt)\s*[:\s\-]*[A-Za-z0-9\s\/\%\.\-\|]+?)(?=(?:Advice|Rx|Diet|Next Review|\d+\.|$|\n|\r))',
                clean_text, re.IGNORECASE
            )
        if vitals_match:
            vt_cand = vitals_match.group(1).strip()
            vt_cand = vt_cand.replace('sp02', 'SpO2').replace('980/0', '98%')
            if len(vt_cand) >= 4:
                vitals = vt_cand

        # 9. Medical Advice & Instructions
        advice = None
        adv_match = re.search(
            r'(?:Medical\s*Advice|Advice|Instructions|Diet\s*\/?\s*Lifestyle|Follow[\-\s]?up|Next\s*Review)\s*[:\s\-]*([A-Za-z0-9\s\,\(\)\-\+\/\.\;\:\'\"\!\?]+?)(?=(?:Emergency|For Appointments|Dr\.|\bReg\b|\Z))',
            clean_text, re.IGNORECASE
        )
        if adv_match:
            av_cand = adv_match.group(1).strip()
            av_cand = re.sub(r'\s+', ' ', av_cand).strip()
            if len(av_cand) >= 4:
                advice = av_cand

        return {
            "hospital": hospital,
            "doctor": doctor_str,
            "patient_name": patient_name,
            "age_gender": age_gender,
            "address": address,
            "allergies": allergies,
            "diagnosis": diagnosis,
            "vitals": vitals,
            "advice": advice,
        }

    def _parse_medicine_line(self, line: str) -> Tuple[Dict[str, Any], float]:
        """
        Parses a single line of prescription text using medical regex patterns.
        """
        working_line = line

        # Strip leading numbers/bullets/Rx
        working_line = re.sub(r'^(?:rx:?\s*|\d+[\.\)\-]?|#\d+)\s*', '', working_line, flags=re.IGNORECASE).strip()

        # 1. Extract Strength (e.g. 500mg, 250 mg, 10ml, 50mcg, 160/4.5mcg)
        strength_match = re.search(r'\b(\d+(?:\/\d+)?(?:\.\d+)?\s*(?:mg|g|mcg|ml|iu|%))\b', working_line, re.IGNORECASE)
        strength = strength_match.group(1) if strength_match else ""
        if strength_match:
            working_line = working_line.replace(strength_match.group(0), " ")

        # 2. Extract Duration (e.g. for 5 days, 1 week, 10d, 6 weeks)
        duration_match = re.search(r'\b(?:for\s*)?(\d+\s*(?:days?|weeks?|months?|d|w|m))\b', working_line, re.IGNORECASE)
        duration = duration_match.group(1) if duration_match else ""
        if duration_match:
            working_line = working_line.replace(duration_match.group(0), " ")

        # 3. Extract Frequency (e.g. 1-0-1, BID, once daily, twice daily, night)
        freq_patterns = [
            r'\b([01]\-[01]\-[01](?:\-[01])?)\b',
            r'\b(once daily|twice daily|thrice daily|four times daily|once a day|twice a day|three times a day|as needed|at night|night|morning)\b',
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

        # 4. Extract Dosage (e.g. 1 tab, 2 capsules, 2 puffs, 5 ml)
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
        cleaned_name = re.sub(r'^(?:tab(?:let)?s?|cap(?:sule)?s?|syp|syrup|inj(?:ection)?s?|ointment|cream|drops?|inhaler)\.?\s+', '', cleaned_name, flags=re.IGNORECASE).strip()

        if not cleaned_name or len(cleaned_name) < 2:
            return {}, 0.0

        unreadable_words = {
            "image", "provide", "assist", "context", "extraction", "transcribe",
            "clearly", "blurry", "resolution", "sorry", "cannot", "could", "would",
            "please", "unclear", "unreadable", "accurate", "accurately", "transcription",
            "small", "help", "information", "further", "reading", "readable"
        }
        name_words_set = set(re.findall(r'[a-zA-Z]+', cleaned_name.lower()))
        if name_words_set & unreadable_words:
            return {}, 0.0

        name_words = cleaned_name.split()
        if len(name_words) > 5 or len(cleaned_name) > 35:
            return {}, 0.0

        has_medical_marker = bool(strength or dosage or frequency or duration)
        known_drug_keywords = (
            "paracetamol", "pcm", "crocin", "calpol", "dolo", "amox", "amoxicillin",
            "ceftas", "drotin", "acera", "alkarate", "lipitor", "atorva", "glucophage",
            "glycomet", "metformin", "shelcal", "zyrtec", "cetirizine", "azee", "azithromycin",
            "pantocid", "pantoprazole", "omeprazole", "cifran", "ciprofloxacin", "budecort",
            "budesonide", "formoterol", "montelukast", "montair", "salbutamol", "asthalin",
            "levocetirizine", "allegra", "fexofenadine", "telmisartan", "amlodipine",
            "dexamethasone", "aspirin", "ibuprofen", "combiflam", "augmentin", "moxikind",
            "telma", "atorvastatin", "rabeprazole", "esomeprazole", "ranitidine"
        )
        has_known_drug = any(k in cleaned_name.lower() for k in known_drug_keywords)

        if not has_medical_marker and not has_known_drug:
            return {}, 0.0

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

        line_l = line.lower()
        form = None
        if "inhaler" in line_l:
            form = "Inhaler"
        elif "tab" in line_l or "tablet" in line_l:
            form = "Tablet"
        elif "cap" in line_l or "capsule" in line_l:
            form = "Capsule"
        elif "syp" in line_l or "syrup" in line_l or "liq" in line_l:
            form = "Syrup"
        elif "inj" in line_l or "injection" in line_l:
            form = "Injection"

        is_ambiguous = (confidence < 0.75 or not strength)

        structured_item = {
            "name": cleaned_name,
            "strength": strength if strength else None,
            "form": form,
            "dosage": dosage if dosage else None,
            "frequency": frequency if frequency else None,
            "duration": duration if duration else None,
            "quantity": quantity if quantity else None,
            "confidence": confidence,
            "raw_evidence_text": line.strip(),
            "is_ambiguous": is_ambiguous,
            "requires_review": is_ambiguous,
        }

        return structured_item, confidence
