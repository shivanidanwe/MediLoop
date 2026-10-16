"""
MediLoop Drug Safety Agent.
Performs clinical safety reviews, drug-drug interaction checks, duplicate ingredient detection,
allergy conflict scanning, and dosage validation.
"""
import re
from typing import Any, Dict, List, Set, Tuple
from app.agents.base_agent import BaseAgent
from app.agents.context import AgentContext
from app.agents.events import AgentEvent
from app.agents.exceptions import AgentValidationError


# Clinical Drug-Drug Interaction Knowledge Base
DRUG_INTERACTIONS: List[Dict[str, Any]] = [
    {
        "drugs": {"warfarin", "aspirin"},
        "severity": "CRITICAL",
        "description": "High risk of severe gastrointestinal hemorrhage and internal bleeding.",
        "recommendation": "Avoid concurrent use; consult prescribing cardiologist immediately.",
        "confidence": 0.98,
    },
    {
        "drugs": {"amoxicillin", "methotrexate"},
        "severity": "HIGH",
        "description": "Penicillins reduce renal clearance of methotrexate, increasing risk of toxicity.",
        "recommendation": "Monitor methotrexate blood levels closely or choose alternative antibiotic.",
        "confidence": 0.94,
    },
    {
        "drugs": {"atorvastatin", "clarithromycin"},
        "severity": "HIGH",
        "description": "Clarithromycin inhibits CYP3A4, markedly increasing statin levels and rhabdomyolysis risk.",
        "recommendation": "Temporarily withhold Atorvastatin during antibiotic course.",
        "confidence": 0.95,
    },
    {
        "drugs": {"metformin", "contrast"},
        "severity": "HIGH",
        "description": "Risk of contrast-induced renal impairment leading to metformin lactic acidosis.",
        "recommendation": "Withhold Metformin prior to intravascular contrast procedures.",
        "confidence": 0.92,
    },
    {
        "drugs": {"aspirin", "ibuprofen"},
        "severity": "MEDIUM",
        "description": "Ibuprofen may attenuate the cardioprotective antiplatelet effect of low-dose Aspirin.",
        "recommendation": "Administer Aspirin 2 hours before or 8 hours after Ibuprofen.",
        "confidence": 0.88,
    },
]

# Allergy Group Drug Cross-Reactivity Mapping
ALLERGY_CROSS_REACTIVITY: Dict[str, List[str]] = {
    "penicillin": ["amoxicillin", "ampicillin", "augmentin", "mox", "penicillin", "amoxil"],
    "sulfa": ["sulfamethoxazole", "bactrim", "septra", "sulfasalazine"],
    "aspirin": ["aspirin", "ecosprin", "disprin", "nsaid"],
    "nsaid": ["ibuprofen", "naproxen", "diclofenac", "combiflam", "brufen"],
}


class DrugSafetyAgent(BaseAgent):
    """
    Clinical Decision Support Agent that analyzes matched & extracted medicines
    for safety risks without altering original prescriptions.
    """

    @property
    def name(self) -> str:
        return "drug_safety_agent"

    @property
    def description(self) -> str:
        return (
            "Performs clinical safety analysis on matched medicines to detect "
            "drug interactions, duplicate active ingredients, allergy conflicts, "
            "dosage limits, and calculates clinical risk levels."
        )

    @property
    def handled_events(self) -> List[AgentEvent]:
        return [
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
                "DrugSafetyAgent validation failed: No medicines available in context to analyze."
            )
        return True

    async def execute(self, context: AgentContext) -> AgentContext:
        """
        Runs clinical safety checks and updates context.metadata['drug_safety'].
        """
        target_medicines = context.matched_medicines if context.matched_medicines else context.extracted_medicines

        warnings: List[Dict[str, Any]] = []
        errors: List[Dict[str, Any]] = []

        # 1. Check Drug-Drug Interactions
        interaction_issues = self._check_drug_interactions(target_medicines)
        for issue in interaction_issues:
            if issue["severity"] in ("CRITICAL", "HIGH"):
                errors.append(issue)
            else:
                warnings.append(issue)

        # 2. Check Duplicate Active Ingredients
        duplicate_issues = self._check_duplicate_ingredients(target_medicines)
        warnings.extend(duplicate_issues)

        # 3. Check Allergy Conflicts against live patient MedicalInfo from DB
        user_allergies: List[str] = context.metadata.get("user_allergies", [])
        customer_id = context.metadata.get("customer_id") or getattr(context, "user_id", None)
        if getattr(context, "db", None) and customer_id:
            try:
                from app.models.medical_info import MedicalInfo
                med_info = context.db.query(MedicalInfo).filter(MedicalInfo.user_id == int(customer_id)).first()
                if med_info and med_info.allergies:
                    user_allergies = [a.strip() for a in med_info.allergies.split(",") if a.strip()]
                    context.metadata["user_allergies"] = user_allergies
            except Exception:
                pass

        if user_allergies is None:
            user_allergies = []

        allergy_issues = self._check_allergy_conflicts(target_medicines, user_allergies)
        errors.extend(allergy_issues)

        # 3.5 Optional Ollama Clinical Reasoning Check
        try:
            from app.core.ollama_client import ollama_client
            med_names = [m.get("name") or m.get("brand_name") or "Unknown" for m in target_medicines]
            prompt = (
                f"Evaluate safety for medicines: {med_names}. Patient Allergies: {user_allergies}.\n"
                f"Return JSON strictly with: 'risk_level' ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL'), 'alert_description' (str), 'recommendation' (str)."
            )
            ai_eval = await ollama_client.generate_json(prompt, system_prompt="You are a clinical pharmacologist safety validator.")
            if ai_eval.get("risk_level") in ("HIGH", "CRITICAL"):
                errors.append({
                    "severity": ai_eval["risk_level"],
                    "description": ai_eval.get("alert_description", "AI identified clinical contraindication risk."),
                    "recommendation": ai_eval.get("recommendation", "Pharmacist review strongly recommended."),
                    "confidence": 0.95
                })
        except Exception:
            pass

        # 4. Check Dosage & Duration Limits
        dosage_issues = self._check_dosage_and_duration(target_medicines)
        warnings.extend(dosage_issues)

        # Calculate Overall Risk Level
        risk_level, status, requires_review = self._calculate_overall_risk(errors, warnings)

        safety_report = {
            "overall_status": status,
            "risk_level": risk_level,
            "total_warnings": len(warnings),
            "total_errors": len(errors),
            "warnings": warnings,
            "errors": errors,
            "requires_pharmacist_review": requires_review,
            "clinical_notes": (
                f"Clinical review completed. Risk level: {risk_level}. "
                f"Requires pharmacist review: {requires_review}."
            ),
        }

        context.metadata["drug_safety"] = safety_report

        # Append alerts to shared context
        for err in errors:
            context.add_warning(f"[{err['severity']} SAFETY ERROR] {err['description']} ({err['recommendation']})")
        for warn in warnings:
            context.add_warning(f"[{warn['severity']} SAFETY WARNING] {warn['description']}")

        if requires_review:
            context.add_recommendation("Mandatory pharmacist verification required prior to dispensing.")

        return context

    def _check_drug_interactions(self, medicines: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Scans prescribed medicine names/generics for drug-drug interactions.
        """
        findings = []
        med_terms: List[Tuple[Dict[str, Any], Set[str]]] = []
        for m in medicines:
            terms = set()
            if m.get("name"):
                terms.add(m["name"].lower())
                terms.add(m["name"].lower().split()[0])
            if m.get("generic_name"):
                terms.add(m["generic_name"].lower())
                terms.add(m["generic_name"].lower().split()[0])
            med_terms.append((m, terms))

        for i in range(len(med_terms)):
            for j in range(i + 1, len(med_terms)):
                m1, terms1 = med_terms[i]
                m2, terms2 = med_terms[j]

                for rule in DRUG_INTERACTIONS:
                    target_pair = rule["drugs"]
                    if any(t in target_pair for t in terms1) and any(t in target_pair for t in terms2):
                        findings.append({
                            "type": "DRUG_INTERACTION",
                            "severity": rule["severity"],
                            "medicines": [m1.get("name"), m2.get("name")],
                            "description": rule["description"],
                            "recommendation": rule["recommendation"],
                            "confidence": rule["confidence"],
                        })
        return findings

    def _check_duplicate_ingredients(self, medicines: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Detects duplicate generic ingredients prescribed under different brand names.
        """
        findings = []
        generic_counts: Dict[str, List[str]] = {}

        for m in medicines:
            gen = m.get("generic_name") or m.get("name")
            if gen and gen != "Unmatched":
                gen_norm = gen.lower()
                generic_counts.setdefault(gen_norm, []).append(m.get("name", gen))

        for gen_name, brand_list in generic_counts.items():
            if len(brand_list) > 1:
                findings.append({
                    "type": "DUPLICATE_INGREDIENT",
                    "severity": "HIGH",
                    "ingredient": gen_name.capitalize(),
                    "brands": brand_list,
                    "description": f"Multiple medicines containing active ingredient '{gen_name.capitalize()}' detected: {', '.join(brand_list)}.",
                    "recommendation": "Review for potential accidental overdosage caused by double therapy.",
                    "confidence": 0.96,
                })
        return findings

    def _check_allergy_conflicts(self, medicines: List[Dict[str, Any]], user_allergies: List[str]) -> List[Dict[str, Any]]:
        """
        Scans prescribed medicines against patient allergy profile.
        """
        findings = []
        for allergy in user_allergies:
            allergy_norm = allergy.lower().strip()
            cross_drugs = ALLERGY_CROSS_REACTIVITY.get(allergy_norm, [allergy_norm])

            for m in medicines:
                m_name = (m.get("name") or "").lower()
                g_name = (m.get("generic_name") or "").lower()

                if any(target in m_name or target in g_name for target in cross_drugs):
                    findings.append({
                        "type": "ALLERGY_CONFLICT",
                        "severity": "CRITICAL",
                        "allergy": allergy,
                        "medicine": m.get("name"),
                        "description": f"Patient has known allergy to '{allergy}'. Prescribed medicine '{m.get('name')}' triggers allergic conflict.",
                        "recommendation": f"Do NOT dispense '{m.get('name')}'. Select non-cross-reactive alternative.",
                        "confidence": 0.98,
                    })
        return findings

    def _check_dosage_and_duration(self, medicines: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Validates max daily dosage and extended duration limits.
        """
        findings = []
        for m in medicines:
            name_lower = (m.get("name") or "").lower()
            strength_str = m.get("strength") or ""
            duration_str = m.get("duration") or ""

            if "paracetamol" in name_lower or "crocin" in name_lower or "dolo" in name_lower:
                match = re.search(r'(\d+)', strength_str)
                if match and int(match.group(1)) >= 650:
                    freq_lower = (m.get("frequency") or "").lower()
                    if "4 times" in freq_lower or "1-1-1-1" in freq_lower:
                        findings.append({
                            "type": "DOSAGE_EXCEEDED",
                            "severity": "HIGH",
                            "medicine": m.get("name"),
                            "description": "Daily Paracetamol dosage exceeds 4000mg maximum safety limit.",
                            "recommendation": "Reduce daily dosing frequency to prevent hepatotoxicity.",
                            "confidence": 0.92,
                        })

            if any(ab in name_lower for ab in ["amoxicillin", "mox", "azithromycin", "azee", "augmentin"]):
                dur_match = re.search(r'(\d+)\s*days?', duration_str, re.IGNORECASE)
                if dur_match and int(dur_match.group(1)) > 14:
                    findings.append({
                        "type": "EXTENDED_DURATION",
                        "severity": "MEDIUM",
                        "medicine": m.get("name"),
                        "description": f"Prescribed antibiotic course ({dur_match.group(1)} days) exceeds standard 14-day limit.",
                        "recommendation": "Confirm extended antibiotic therapy intent with prescribing physician.",
                        "confidence": 0.85,
                    })

        return findings

    def _calculate_overall_risk(
        self, errors: List[Dict[str, Any]], warnings: List[Dict[str, Any]]
    ) -> Tuple[str, str, bool]:
        """Calculates clinical risk score, overall status, and pharmacist review flag."""
        has_critical = any(e.get("severity") == "CRITICAL" for e in errors + warnings)
        has_high = any(e.get("severity") == "HIGH" for e in errors + warnings)
        has_medium = any(w.get("severity") == "MEDIUM" for w in warnings)

        if has_critical:
            return "CRITICAL", "CRITICAL_WARNING", True
        if has_high:
            return "HIGH", "REQUIRES_REVIEW", True
        if has_medium:
            return "MEDIUM", "CAUTION", False
        return "LOW", "SAFE", False
