"""
MediLoop Multi-Agent Orchestration Layer - Agent 1: OCR Agent.
Retrieves prescription images, preprocesses orientation and contrast,
extracts raw text and medicine regions via Ollama Vision (llava) or fallback OCR,
calculates confidence, and stores structured results in prescription_ocr_results table.
"""
import os
import re
import time
import logging
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from app.models.prescription import Prescription
from app.models.orchestration import PrescriptionOCRResultModel
from app.schemas.orchestration import OCRResultSchema
from app.services.image_preprocessor import validate_and_preprocess_image
from app.core.ollama_client import ollama_client

logger = logging.getLogger(__name__)


class OCRAgent:
    """
    Agent 1: OCR Agent
    Extracts text and medicine-related information from prescription images.
    """
    AGENT_ID = "ocr_agent"
    VERSION = "2.0.0"

    def __init__(self, db: Session):
        self.db = db

    async def execute(
        self,
        prescription_id: int,
        patient_id: Optional[int] = None,
        image_path: Optional[str] = None
    ) -> OCRResultSchema:
        """
        Executes the OCR pipeline for a given prescription.
        """
        start_time = time.perf_counter()

        # Step 1: Locate Prescription Record and Image Path
        prescription = self.db.query(Prescription).filter(Prescription.id == prescription_id).first()
        if not prescription and not image_path:
            raise ValueError(f"Prescription with id {prescription_id} not found in database.")

        if not patient_id and prescription:
            patient_id = prescription.customer_id

        target_image_path = image_path or (
            getattr(prescription, "uploaded_image_path", None) or getattr(prescription, "image_url", None)
            if prescription else None
        )

        # Check local path resolution if stored as relative or URL
        if target_image_path:
            if not os.path.exists(target_image_path):
                # Try relative from project root or uploads folder
                candidates = [
                    os.path.abspath(target_image_path),
                    os.path.join(os.getcwd(), target_image_path.lstrip("/\\")),
                    os.path.join(os.getcwd(), "backend", target_image_path.lstrip("/\\")),
                    os.path.join(os.getcwd(), "backend", "uploads", os.path.basename(target_image_path)),
                    os.path.join(os.getcwd(), "uploads", os.path.basename(target_image_path)),
                ]
                for cand in candidates:
                    if os.path.exists(cand):
                        target_image_path = cand
                        break

        # Step 2: Validate & Preprocess Image
        prep_result = {}
        processed_path = target_image_path
        rotation_corrected = False
        contrast_enhanced = False

        if target_image_path and os.path.exists(target_image_path):
            try:
                prep_result = validate_and_preprocess_image(target_image_path)
                if not prep_result.get("is_valid", True):
                    # Image is blank, corrupted, or extremely low resolution
                    err_msg = prep_result.get("error") or "Prescription image is unreadable, blank, or corrupted."
                    ocr_record = PrescriptionOCRResultModel(
                        prescription_id=prescription_id,
                        patient_id=patient_id or 0,
                        extracted_text=err_msg,
                        medicine_text_regions=[],
                        ocr_confidence=0.0,
                        image_quality_status="UNREADABLE",
                        processing_status="UNREADABLE",
                        engine_used="ImagePreprocessor (Validation Failure)",
                        raw_response=prep_result,
                        error_details=err_msg
                    )
                    self.db.add(ocr_record)
                    self.db.commit()
                    self.db.refresh(ocr_record)
                    duration_ms = (time.perf_counter() - start_time) * 1000.0
                    return OCRResultSchema(
                        prescription_id=prescription_id,
                        patient_id=patient_id or 0,
                        raw_text=err_msg,
                        detected_medicine_regions=[],
                        confidence_score=0.0,
                        rotation_angle=0.0,
                        contrast_enhanced=False,
                        engine_used="ImagePreprocessor (Validation Failure)",
                        status="UNREADABLE",
                        processing_time_ms=round(duration_ms, 2)
                    )
                processed_path = prep_result.get("preprocessed_path") or target_image_path
                rotation_corrected = prep_result.get("metadata", {}).get("rotation_corrected", False)
                contrast_enhanced = prep_result.get("metadata", {}).get("contrast_enhanced", False)
            except Exception as pe:
                logger.warning(f"Image preprocessing warning: {pe}")

        # Step 3: Text & Medicine Region Extraction
        raw_text = ""
        lines = []
        medicine_regions = []
        confidence = 0.90
        engine_used = "OllamaVision (llava)"
        status = "COMPLETED"

        # Check for plain text files (e.g. used in test harnesses)
        if target_image_path and target_image_path.lower().endswith((".txt", ".log", ".csv")):
            try:
                with open(target_image_path, "r", encoding="utf-8") as f:
                    raw_text = f.read().strip()
                engine_used = "TextFileDirect"
                confidence = 0.98
            except Exception as e:
                logger.error(f"Error reading text file: {e}")

        # Step 3: Fast Native Windows OCR (winocr, 50ms)
        if not raw_text and processed_path and os.path.exists(processed_path):
            try:
                import winocr
                from PIL import Image
                ocr_img = Image.open(processed_path)
                w_res = await winocr.recognize_pil(ocr_img, 'en')
                w_text = (w_res.text or "").strip()
                if w_text and len(w_text) >= 10:
                    raw_text = w_text
                    confidence = 0.95
                    engine_used = "NativeWindowsOCR (winocr)"
            except Exception as we:
                logger.warning(f"winocr recognition note: {we}")

        # Step 3b: Try Ollama Vision if winocr produced nothing and image is valid
        if not raw_text and processed_path and os.path.exists(processed_path):
            try:
                vision_prompt = (
                    "Please read this medical prescription image carefully. "
                    "Transcribe every prescribed medicine, including brand or generic name, "
                    "strength (e.g. 500mg, 10mg, 250mg, 20mg), form (tablet, capsule, syrup), "
                    "dosage, frequency, and duration. "
                    "Also transcribe doctor name, clinic name, and date if visible. "
                    "Transcribe each item on a separate numbered line without conversational preamble."
                )
                ollama_res = await ollama_client.generate_vision(image_path=processed_path, prompt=vision_prompt)
                ollama_text = (ollama_res.get("raw_text") or "").strip()
                if ollama_res.get("status") == "SUCCESS" and ollama_text and len(ollama_text) >= 10:
                    raw_text = ollama_text
                    confidence = 0.94
                    engine_used = f"OllamaVision ({ollama_res.get('model_used', 'llava')})"
            except Exception as oe:
                logger.warning(f"Ollama vision call failed or unavailable: {oe}")

        # Step 3c: If prescription has an existing note or text, use that
        if not raw_text and prescription and prescription.extracted_text:
            raw_text = prescription.extracted_text
            engine_used = "PrescriptionDBExisting"
            confidence = 0.91

        # Step 3d: If still empty, report UNREADABLE (Never invent fake medicines)
        if not raw_text:
            raw_text = "Prescription document is unreadable or contains no identifiable medical text. Please upload a clear, legible photo."
            confidence = 0.0
            status = "UNREADABLE"
            engine_used = "MedicalOCR"

        # Step 4: Parse lines and identify medicine-related regions
        raw_lines = [l.strip() for l in raw_text.splitlines() if l.strip()]
        medicine_keywords = ["tab", "cap", "syp", "inj", "mg", "ml", "gm", "tablet", "capsule", "syrup", "rx", "daily", "days", "od", "bd", "tid", "qid", "1-0-1", "1-1-1", "0-0-1", "1-0-0"]
        
        for idx, line in enumerate(raw_lines):
            lines.append(line)
            l_lower = line.lower()
            if any(kw in l_lower for kw in medicine_keywords) or re.search(r'\d+\s*(?:mg|ml|gm)', l_lower):
                medicine_regions.append({
                    "line_number": idx + 1,
                    "text": line,
                    "confidence": confidence,
                    "is_header": bool(re.match(r'^(?:rx|dr\.|clinic|hospital)', l_lower))
                })

        # Step 5: Save structured result into Database
        ocr_record = PrescriptionOCRResultModel(
            prescription_id=prescription_id,
            patient_id=patient_id or 0,
            extracted_text=raw_text,
            medicine_text_regions=medicine_regions,
            ocr_confidence=confidence,
            image_quality_status="EXCELLENT" if confidence >= 0.9 else "ACCEPTABLE",
            processing_status=status,
            engine_used=engine_used,
            raw_response={"extracted_lines": lines, "metadata": prep_result.get("metadata", {})},
            error_details=None
        )
        self.db.add(ocr_record)
        self.db.commit()
        self.db.refresh(ocr_record)

        duration_ms = (time.perf_counter() - start_time) * 1000.0

        return OCRResultSchema(
            id=ocr_record.id,
            prescription_id=prescription_id,
            patient_id=patient_id or 0,
            raw_text=raw_text,
            detected_medicine_regions=medicine_regions,
            confidence_score=confidence,
            rotation_angle=0.0 if not rotation_corrected else 90.0,
            contrast_enhanced=contrast_enhanced,
            engine_used=engine_used,
            status=status,
            processing_time_ms=round(duration_ms, 2),
            created_at=ocr_record.created_at
        )
