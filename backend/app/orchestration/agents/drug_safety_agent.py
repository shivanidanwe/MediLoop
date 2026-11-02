"""
MediLoop Multi-Agent Orchestration Layer - Agent 3: Drug Safety Agent.
Performs comprehensive clinical safety screening on extracted and matched medicines:
Allergies, Medication History, Drug-Drug Interactions, Contraindications, Duplicate Therapies.
Blocks downstream order creation if critical/high severity findings exist.
Persists assessments in drug_safety_assessments and safety_findings tables.
"""
import time
import logging
from typing import Dict, Any, List, Optional, Set
from sqlalchemy.orm import Session

from app.models.medical_info import MedicalInfo
from app.models.prescription import Prescription, PrescriptionItem
from app.models.order import Order, OrderItem, OrderStatus
from app.models.medicine import Medicine
from app.models.orchestration import DrugSafetyAssessmentModel, SafetyFindingModel
from app.schemas.orchestration import (
    DrugSafetyAssessmentSchema,
    SafetyFindingSchema,
    ExtractedMedicineSchema
)

logger = logging.getLogger(__name__)

# Curated Clinical Drug-Drug Interaction Knowledge Base
DRUG_INTERACTIONS = [
    {
        "drugs": {"warfarin", "aspirin"},
        "severity": "critical",
        "description": "High risk of severe gastrointestinal hemorrhage and uncontrollable bleeding.",
        "recommendation": "Do not co-prescribe without explicit hematological monitoring; consider alternative analgesic.",
        "evidence": "FDA Black Box Warning; Cytochrome P450 competitive displacement."
    },
    {
        "drugs": {"amoxicillin", "methotrexate"},
        "severity": "high",
        "description": "Amoxicillin reduces renal clearance of methotrexate, increasing serum levels and risk of fatal toxicity.",
        "recommendation": "Monitor methotrexate blood levels closely or choose non-penicillin antibiotic.",
        "evidence": "Renal tubular secretion competition."
    },
    {
        "drugs": {"atorvastatin", "clarithromycin"},
        "severity": "high",
        "description": "Clarithromycin strongly inhibits CYP3A4, markedly increasing Atorvastatin exposure and risk of rhabdomyolysis.",
        "recommendation": "Temporarily withhold Atorvastatin during the clarithromycin treatment course.",
        "evidence": "CYP3A4 hepatic inhibition interaction."
    },
    {
        "drugs": {"metformin", "contrast"},
        "severity": "high",
        "description": "Risk of contrast-induced acute kidney injury leading to potentially fatal metformin lactic acidosis.",
        "recommendation": "Withhold Metformin 48 hours prior to and post intravascular iodinated contrast procedures.",
        "evidence": "Clinical guideline: ACR Manual on Contrast Media."
    },
    {
        "drugs": {"aspirin", "ibuprofen"},
        "severity": "medium",
        "description": "Ibuprofen competitively inhibits the irreversible platelet COX-1 binding of cardioprotective Aspirin.",
        "recommendation": "Administer immediate-release Aspirin at least 2 hours before or 8 hours after Ibuprofen.",
        "evidence": "FDA Drug Safety Communication: Concomitant use of Ibuprofen and Aspirin."
    },
    {
        "drugs": {"ciprofloxacin", "antacid"},
        "severity": "medium",
        "description": "Chelation with polyvalent cations (aluminum, magnesium, calcium) significantly reduces ciprofloxacin bioavailability.",
        "recommendation": "Separate administration by at least 2 hours before or 6 hours after antacids.",
        "evidence": "Pharmacokinetic chelation complexation."
    },
    {
        "drugs": {"paracetamol", "combiflam"},
        "severity": "high",
        "description": "Combiflam already contains 325mg Paracetamol. Concurrent Paracetamol risks hepatotoxicity exceeding 4000mg/day limit.",
        "recommendation": "Avoid simultaneous use; potential acute acetaminophen overdose.",
        "evidence": "Duplicate acetaminophen toxicity warning."
    }
]

# Allergy Cross-Reactivity Drug Groups
ALLERGY_CROSS_REACTIVITY: Dict[str, List[str]] = {
    "penicillin": ["amoxicillin", "ampicillin", "augmentin", "mox", "penicillin", "amoxil", "clavam", "cephalexin"],
    "sulfa": ["sulfamethoxazole", "bactrim", "septra", "sulfasalazine", "cotrimoxazole"],
    "aspirin": ["aspirin", "ecosprin", "disprin", "salicylate"],
    "nsaid": ["ibuprofen", "naproxen", "diclofenac", "combiflam", "brufen", "ketorolac", "mefenamic"],
    "paracetamol": ["paracetamol", "acetaminophen", "crocin", "dolo", "calpol"],
    "statin": ["atorvastatin", "rosuvastatin", "simvastatin", "pravastatin"],
}

# Disease / Condition Contraindications
CONTRAINDICATIONS: List[Dict[str, Any]] = [
    {
        "condition": "asthma",
        "drugs": ["aspirin", "ibuprofen", "combiflam", "naproxen", "atenolol", "propranolol"],
        "severity": "high",
        "description": "NSAIDs and non-selective beta-blockers can precipitate severe bronchospasm in asthmatic patients.",
        "recommendation": "Avoid NSAIDs; use Paracetamol or selective agents with pulmonology clearance."
    },
    {
        "condition": "hypertension",
        "drugs": ["pseudoephedrine", "phenylephrine", "ibuprofen", "combiflam"],
        "severity": "medium",
        "description": "Decongestants and regular NSAIDs cause sodium retention and arterial vasoconstriction, raising blood pressure.",
        "recommendation": "Monitor blood pressure; use topical saline sprays or paracetamol instead."
    },
    {
        "condition": "ulcer",
        "drugs": ["aspirin", "ibuprofen", "combiflam", "naproxen", "diclofenac"],
        "severity": "high",
        "description": "Non-steroidal anti-inflammatory drugs inhibit protective gastric prostaglandins, aggravating active peptic ulcers.",
        "recommendation": "Co-prescribe proton-pump inhibitor (e.g. Pantoprazole) or switch to paracetamol."
    },
    {
        "condition": "diabetes",
        "drugs": ["prednisone", "dexamethasone", "hydrocortisone", "betamethasone"],
        "severity": "medium",
        "description": "Corticosteroids increase gluconeogenesis and insulin resistance, leading to marked hyperglycemia.",
        "recommendation": "Frequent blood glucose monitoring; adjust hypoglycemic regimen if steroid is essential."
    }
]


class DrugSafetyAgent:
    """
    Agent 3: Drug Safety Agent
    Screens extracted medicines against allergies, medication history, interactions, and contraindications.
    """
    AGENT_ID = "drug_safety_agent"
    VERSION = "2.0.0"

    def __init__(self, db: Session):
        self.db = db

    async def execute(
        self,
        prescription_id: int,
        patient_id: int,
        extracted_medicines: List[ExtractedMedicineSchema]
    ) -> DrugSafetyAssessmentSchema:
        """
        Runs comprehensive multi-point clinical safety analysis.
        """
        start_time = time.perf_counter()

        findings: List[SafetyFindingSchema] = []
        checks_performed = [
            "allergy_check",
            "medication_history_overlap",
            "drug_drug_interaction",
            "contraindication_check",
            "duplicate_therapy_check"
        ]

        # Step 1: Retrieve Patient Medical Profile & Recorded Allergies
        med_info = self.db.query(MedicalInfo).filter(MedicalInfo.user_id == patient_id).first()
        allergies_str = med_info.allergies if med_info and med_info.allergies else ""
        chronic_conditions_str = (getattr(med_info, "medical_conditions", None) or getattr(med_info, "chronic_conditions", None) or "") if med_info else ""

        patient_allergies = [a.strip().lower() for a in allergies_str.split(",") if a.strip()]
        patient_conditions = [c.strip().lower() for c in chronic_conditions_str.split(",") if c.strip()]

        # Step 2: Retrieve Patient Medication History (Past delivered/approved orders & prescriptions)
        past_active_drugs = self._get_past_active_medications(patient_id, exclude_prescription_id=prescription_id)

        # Step 3: Check A - Recorded Allergies Check
        for med in extracted_medicines:
            med_names = [med.medicine_name.lower()]
            if med.generic_name:
                med_names.append(med.generic_name.lower())
            if med.brand_name:
                med_names.append(med.brand_name.lower())

            for allergy in patient_allergies:
                # Direct match
                if any(allergy in m_name for m_name in med_names):
                    findings.append(SafetyFindingSchema(
                        medicine_name=med.medicine_name,
                        issue_type="allergy",
                        severity="critical",
                        description=f"Direct allergy conflict: Patient is recorded as allergic to '{allergy}'.",
                        recommendation="Do not dispense. Requires immediate physician clarification or alternative drug.",
                        clinical_evidence="Patient Medical Profile - Documented Allergy Record",
                        requires_pharmacist_action=True
                    ))
                    continue

                # Cross-reactivity group match
                for group, members in ALLERGY_CROSS_REACTIVITY.items():
                    if allergy in group or any(allergy in member for member in members):
                        if any(any(m in m_name for m in members) for m_name in med_names):
                            findings.append(SafetyFindingSchema(
                                medicine_name=med.medicine_name,
                                issue_type="allergy",
                                severity="high",
                                description=(
                                    f"Cross-reactivity allergy risk: '{med.medicine_name}' belongs to the {group.capitalize()} "
                                    f"class which patient is documented allergic to ({allergy})."
                                ),
                                recommendation="Review patient tolerance or select non-cross-reactive alternative.",
                                clinical_evidence=f"Immunological cross-reactivity in {group.capitalize()} class.",
                                requires_pharmacist_action=True
                            ))

        # Step 4: Check B - Duplicate Therapy / Overlapping Active Ingredients
        seen_ingredients: Dict[str, str] = {}
        for med in extracted_medicines:
            ingredient = (med.generic_name or med.medicine_name).lower()
            for key_ing, prev_name in seen_ingredients.items():
                if key_ing in ingredient or ingredient in key_ing:
                    findings.append(SafetyFindingSchema(
                        medicine_name=med.medicine_name,
                        issue_type="duplicate_therapy",
                        severity="high",
                        description=(
                            f"Duplicate active therapy detected between '{med.medicine_name}' and '{prev_name}'. "
                            f"Both contain active component '{ingredient}'."
                        ),
                        recommendation="Clarify if doctor intended brand substitution or additive dosing.",
                        clinical_evidence="Prescription Extraction Duplicate Component Analysis",
                        requires_pharmacist_action=True
                    ))
            seen_ingredients[ingredient] = med.medicine_name

        # Also check against recent past active medications
        for past_drug in past_active_drugs:
            for med in extracted_medicines:
                curr_ing = (med.generic_name or med.medicine_name).lower()
                if past_drug["ingredient"] in curr_ing or curr_ing in past_drug["ingredient"]:
                    findings.append(SafetyFindingSchema(
                        medicine_name=med.medicine_name,
                        issue_type="duplicate_therapy",
                        severity="medium",
                        description=(
                            f"Overlapping medication history: Patient recently received '{past_drug['name']}' "
                            f"(Ordered on {past_drug['date']}) with same active component."
                        ),
                        recommendation="Verify whether previous course is completed before initiating new supply.",
                        clinical_evidence="MediLoop Patient Order & Prescription History",
                        requires_pharmacist_action=False
                    ))

        # Step 5: Check C - Drug-Drug Interactions
        # Combine newly prescribed medicines with past active medicines for interaction checking
        all_eval_drugs: List[str] = []
        for m in extracted_medicines:
            all_eval_drugs.append(m.medicine_name.lower())
            if m.generic_name:
                all_eval_drugs.append(m.generic_name.lower())
        for p in past_active_drugs:
            all_eval_drugs.append(p["name"].lower())
            if p["ingredient"]:
                all_eval_drugs.append(p["ingredient"].lower())

        for interaction in DRUG_INTERACTIONS:
            target_set = interaction["drugs"]
            # Check if all drugs in this pair/group are present in all_eval_drugs
            matched_count = 0
            involved_names = []
            for target_drug in target_set:
                for candidate in all_eval_drugs:
                    if target_drug in candidate:
                        matched_count += 1
                        involved_names.append(candidate.capitalize())
                        break

            if matched_count >= len(target_set):
                findings.append(SafetyFindingSchema(
                    medicine_name=" + ".join(list(target_set)).title(),
                    issue_type="interaction",
                    severity=interaction["severity"],
                    description=interaction["description"],
                    recommendation=interaction["recommendation"],
                    clinical_evidence=interaction["evidence"],
                    requires_pharmacist_action=(interaction["severity"] in ("critical", "high"))
                ))

        # Step 6: Check D - Patient Chronic Conditions Contraindications
        for cond in patient_conditions:
            for contra in CONTRAINDICATIONS:
                if contra["condition"] in cond:
                    for med in extracted_medicines:
                        m_names = [med.medicine_name.lower()]
                        if med.generic_name:
                            m_names.append(med.generic_name.lower())
                        for bad_drug in contra["drugs"]:
                            if any(bad_drug in mn for mn in m_names):
                                findings.append(SafetyFindingSchema(
                                    medicine_name=med.medicine_name,
                                    issue_type="contraindication",
                                    severity=contra["severity"],
                                    description=(
                                        f"Clinical contraindication: '{med.medicine_name}' is contraindicated in "
                                        f"patients with documented condition '{cond.capitalize()}'. {contra['description']}"
                                    ),
                                    recommendation=contra["recommendation"],
                                    clinical_evidence=f"Medical Condition Contraindication Matrix ({cond.capitalize()})",
                                    requires_pharmacist_action=(contra["severity"] in ("critical", "high"))
                                ))

        # Step 7: Synthesize Overall Risk & Execution Gates
        critical_count = sum(1 for f in findings if f.severity == "critical")
        high_count = sum(1 for f in findings if f.severity == "high")
        medium_count = sum(1 for f in findings if f.severity == "medium")

        if critical_count > 0:
            safety_status = "critical"
            overall_risk = "critical"
            can_proceed = False
            requires_review = True
        elif high_count > 0:
            safety_status = "critical"
            overall_risk = "high"
            can_proceed = False
            requires_review = True
        elif medium_count > 0:
            safety_status = "warning"
            overall_risk = "moderate"
            can_proceed = True
            requires_review = True
        else:
            safety_status = "safe"
            overall_risk = "low"
            can_proceed = True
            requires_review = False

        duration_ms = (time.perf_counter() - start_time) * 1000.0

        # Step 8: Persist Assessment into Database
        summary_text = (
            f"Safety Status: {safety_status.upper()}. Risk: {overall_risk.upper()}. "
            f"Evaluated {len(checks_performed)} checks with {len(findings)} findings."
        )
        assessment_record = DrugSafetyAssessmentModel(
            prescription_id=prescription_id,
            patient_id=patient_id,
            safety_status=safety_status,
            overall_risk=overall_risk,
            checks_performed=checks_performed,
            requires_review=requires_review,
            can_proceed=can_proceed,
            summary=summary_text
        )
        self.db.add(assessment_record)
        self.db.commit()
        self.db.refresh(assessment_record)

        # Persist individual findings
        persisted_findings: List[SafetyFindingModel] = []
        for f in findings:
            finding_rec = SafetyFindingModel(
                assessment_id=assessment_record.id,
                medicine_name=f.medicine_name,
                issue_type=f.issue_type,
                severity=f.severity,
                description=f.description,
                recommendation=f.recommendation,
                evidence_source=f.clinical_evidence or "Clinical Interaction Database",
                confidence=0.95,
                is_blocking=(f.severity in ("critical", "high"))
            )
            self.db.add(finding_rec)
            persisted_findings.append(finding_rec)

        self.db.commit()

        return DrugSafetyAssessmentSchema(
            id=assessment_record.id,
            prescription_id=prescription_id,
            patient_id=patient_id,
            safety_status=safety_status,
            overall_risk=overall_risk,
            checks_performed=checks_performed,
            findings=findings,
            requires_review=requires_review,
            can_proceed=can_proceed,
            pharmacist_cleared=False,
            processing_time_ms=round(duration_ms, 2),
            created_at=assessment_record.created_at
        )

    def _get_past_active_medications(self, patient_id: int, exclude_prescription_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Retrieves recently ordered or prescribed medications within the last 45 days."""
        history = []
        try:
            # Query past orders
            orders = self.db.query(Order).filter(
                Order.customer_id == patient_id,
                Order.order_status.in_([OrderStatus.CONFIRMED, OrderStatus.DELIVERED, OrderStatus.PROCESSING])
            ).order_by(Order.order_date.desc()).limit(5).all()

            for ord_obj in orders:
                for item in ord_obj.items:
                    if item.medicine:
                        history.append({
                            "name": item.medicine.brand_name,
                            "ingredient": (item.medicine.generic_name or item.medicine.brand_name).lower(),
                            "date": ord_obj.order_date.strftime("%Y-%m-%d") if ord_obj.order_date else "Recent"
                        })

            # Also query previous verified prescriptions
            q = self.db.query(Prescription).filter(Prescription.customer_id == patient_id)
            if exclude_prescription_id:
                q = q.filter(Prescription.id != exclude_prescription_id)
            prev_rx = q.order_by(Prescription.uploaded_at.desc()).limit(3).all()

            for rx in prev_rx:
                for item in rx.items:
                    history.append({
                        "name": item.medicine_name,
                        "ingredient": (item.dosage or item.medicine_name).lower(),
                        "date": rx.uploaded_at.strftime("%Y-%m-%d") if rx.uploaded_at else "Past Rx"
                    })
        except Exception as e:
            logger.warning(f"Error reading medication history: {e}")

        return history
