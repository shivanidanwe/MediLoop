"""
MediLoop OCR Agent & Provider Abstraction.
Extracts raw text from uploaded prescription images without altering or interpreting text.
"""
from abc import ABC, abstractmethod
import os
import re
import time
from typing import Any, Dict, List, Optional
from app.agents.base_agent import BaseAgent
from app.agents.context import AgentContext
from app.agents.events import AgentEvent
from app.agents.exceptions import AgentValidationError


class BaseOCRProvider(ABC):
    """
    Abstract Interface for OCR Engine Providers (e.g. Gemini Vision, Tesseract, Azure, AWS Textract).
    """

    @property
    @abstractmethod
    def engine_name(self) -> str:
        """Returns the identifier name of the underlying OCR provider engine."""
        pass

    @abstractmethod
    async def process_image(self, image_path: str) -> Dict[str, Any]:
        """
        Processes an image file path and returns a dictionary containing raw_text, lines, confidence, and metadata.
        """
        pass


class MedicalVisionOCRProvider(BaseOCRProvider):
    """
    Default MediLoop Medical Vision OCR Provider.
    Extracts raw text from prescription image files, supporting image reading & fallback mock processing for dev environments.
    """

    @property
    def engine_name(self) -> str:
        return "MedicalVisionOCRProvider"

    async def process_image(self, image_path: str) -> Dict[str, Any]:
        start_time = time.perf_counter()

        # Step 0: Robust Path Resolution
        target_image_path = image_path
        if not target_image_path or not os.path.exists(target_image_path):
            candidates = [
                image_path,
                os.path.abspath(image_path or ""),
                os.path.join(os.getcwd(), (image_path or "").lstrip("/\\")),
                os.path.join(os.getcwd(), "backend", (image_path or "").lstrip("/\\")),
                os.path.join(os.getcwd(), "uploads", "prescriptions", os.path.basename(image_path or "")),
                os.path.join(os.getcwd(), "backend", "uploads", "prescriptions", os.path.basename(image_path or "")),
            ]
            for c in candidates:
                if c and os.path.exists(c) and os.path.isfile(c):
                    target_image_path = c
                    break

        if not target_image_path or not os.path.exists(target_image_path):
            duration = (time.perf_counter() - start_time) * 1000.0
            return {
                "raw_text": "Prescription document file not found on server storage.",
                "lines": [],
                "language": "en",
                "confidence": 0.0,
                "status": "FILE_NOT_FOUND",
                "engine_used": "MedicalVisionOCRProvider",
                "duration_ms": round(duration, 2),
            }

        # Step 1: Text-based files (used in test harnesses)
        if target_image_path.lower().endswith((".txt", ".log", ".csv")):
            try:
                with open(target_image_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read().strip().replace("\x00", "")
                if content:
                    lines = [line.strip() for line in content.splitlines() if line.strip()]
                    duration = (time.perf_counter() - start_time) * 1000.0
                    return {
                        "raw_text": content,
                        "lines": lines,
                        "language": "en",
                        "confidence": 0.98,
                        "engine_used": "TextFileReader",
                        "duration_ms": round(duration, 2),
                    }
            except Exception:
                pass

        # Step 2: Image Preprocessing (orientation, contrast, blank detection)
        preprocessed_path = target_image_path
        try:
            from app.services.image_preprocessor import validate_and_preprocess_image
            prep = validate_and_preprocess_image(target_image_path)
            if not prep.get("is_valid", True):
                duration = (time.perf_counter() - start_time) * 1000.0
                return {
                    "raw_text": prep.get("error") or "Prescription image is unreadable, blurry, or blank. Please upload a clear photo.",
                    "lines": [],
                    "language": "en",
                    "confidence": 0.0,
                    "status": "UNREADABLE",
                    "engine_used": "MedicalVisionOCRProvider (Image Preprocessor)",
                    "duration_ms": round(duration, 2),
                    "preprocessing": prep
                }
            preprocessed_path = prep.get("preprocessed_path") or target_image_path
        except Exception:
            preprocessed_path = target_image_path

        # Step 3: Tier 1 - Fast Native Windows OCR (winocr, 50ms execution)
        try:
            import winocr
            from PIL import Image
            ocr_img = Image.open(preprocessed_path)
            res = await winocr.recognize_pil(ocr_img, 'en')
            raw_extracted = (res.text or "").strip()
            ocr_lines = [l.text.strip() for l in res.lines if l.text and l.text.strip()]

            if raw_extracted and len(raw_extracted) >= 10:
                duration = (time.perf_counter() - start_time) * 1000.0
                return {
                    "raw_text": raw_extracted,
                    "lines": ocr_lines if ocr_lines else [raw_extracted],
                    "language": "en",
                    "confidence": 0.95,
                    "engine_used": "NativeWindowsOCR (winocr)",
                    "duration_ms": round(duration, 2),
                }
        except Exception:
            pass

        # Step 4: Tier 2 - Multimodal Ollama Vision (llava:latest)
        try:
            from app.core.ollama_client import ollama_client
            prompt = (
                "Please read this medical prescription image carefully. "
                "Transcribe every prescribed medicine, including brand or generic name, "
                "strength (e.g. 500mg, 10mg, 250mg, 20mg), form (tablet, capsule, syrup), "
                "dosage, frequency, and duration. "
                "Also transcribe any doctor name, clinic name, or patient details if visible. "
                "Transcribe each item on a separate numbered line without conversational preamble."
            )
            ollama_res = await ollama_client.generate_vision(image_path=preprocessed_path, prompt=prompt)
            raw_text_full = (ollama_res.get("raw_text") or "").strip()

            if ollama_res.get("status") == "SUCCESS" and raw_text_full and len(raw_text_full) >= 10:
                # Clean out conversational disclaimers
                disclaimer_patterns = [
                    r"^it is important to note that.*$",
                    r"^please note that.*$",
                    r"^sharing personal medical information.*$",
                    r"^without additional context.*$",
                    r"^if you have any questions.*$",
                    r"^i would be happy to assist.*$",
                    r"^the image appears to be.*$",
                    r"^here is the transcription.*$",
                    r"^as an ai language model.*$",
                ]
                cleaned_lines = []
                for line in raw_text_full.splitlines():
                    trimmed = line.strip()
                    if not trimmed or trimmed == "```":
                        continue
                    if any(re.match(p, trimmed.lower()) for p in disclaimer_patterns):
                        continue
                    cleaned_lines.append(trimmed)

                clean_text = "\n".join(cleaned_lines) if cleaned_lines else raw_text_full
                duration = (time.perf_counter() - start_time) * 1000.0
                return {
                    "raw_text": clean_text,
                    "lines": cleaned_lines if cleaned_lines else [clean_text],
                    "language": "en",
                    "confidence": 0.94,
                    "engine_used": f"Ollama ({ollama_res.get('model_used')})",
                    "duration_ms": round(duration, 2),
                }
        except Exception:
            pass

        # Step 5: If no text could be extracted, return UNREADABLE (Never invent fake medicines)
        duration = (time.perf_counter() - start_time) * 1000.0
        return {
            "raw_text": "Prescription document is unreadable or contains no identifiable medical text. Please upload a clear, legible photo.",
            "lines": [],
            "language": "en",
            "confidence": 0.0,
            "status": "UNREADABLE",
            "engine_used": "MedicalVisionOCRProvider",
            "duration_ms": round(duration, 2),
        }


class OCRAgent(BaseAgent):
    """
    Independent OCR Agent responsible ONLY for extracting raw text from prescription scan images.
    """

    def __init__(self, ocr_provider: Optional[BaseOCRProvider] = None):
        self.ocr_provider = ocr_provider or MedicalVisionOCRProvider()

    @property
    def name(self) -> str:
        return "ocr_agent"

    @property
    def description(self) -> str:
        return "Extracts raw text from uploaded prescription scan images using configured OCR engine provider."

    @property
    def handled_events(self) -> List[AgentEvent]:
        return [AgentEvent.PRESCRIPTION_UPLOADED]

    async def can_handle(self, event: AgentEvent, context: AgentContext) -> bool:
        """
        Agent handles PRESCRIPTION_UPLOADED when an uploaded image path is present.
        """
        return event == AgentEvent.PRESCRIPTION_UPLOADED and bool(context.uploaded_image)

    async def validate(self, context: AgentContext) -> bool:
        """
        Validates uploaded image presence and format before execution.
        """
        if not context.uploaded_image or not isinstance(context.uploaded_image, str):
            raise AgentValidationError(
                "OCRAgent validation failed: 'uploaded_image' is missing or invalid in context."
            )

        valid_extensions = ('.png', '.jpg', '.jpeg', '.pdf', '.webp', '.tiff', '.bmp')
        ext = os.path.splitext(context.uploaded_image)[1].lower()
        if ext and ext not in valid_extensions:
            raise AgentValidationError(
                f"OCRAgent validation failed: Unsupported image extension '{ext}'. Allowed: {valid_extensions}"
            )

        return True

    async def execute(self, context: AgentContext) -> AgentContext:
        """
        Extracts raw text using OCR provider and updates shared context.
        """
        image_path = context.uploaded_image or ""
        ocr_result = await self.ocr_provider.process_image(image_path)

        context.ocr_text = ocr_result.get("raw_text", "")
        context.metadata["ocr"] = ocr_result

        confidence = ocr_result.get("confidence", 1.0)
        if confidence < 0.75:
            context.add_warning(
                f"Low OCR confidence ({confidence:.2f}) reported by '{ocr_result.get('engine_used')}'."
            )

        return context
