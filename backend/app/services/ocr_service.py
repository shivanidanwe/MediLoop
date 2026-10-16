from abc import ABC, abstractmethod
from typing import Tuple
import random

class OCRAngine(ABC):
    @abstractmethod
    def extract_text(self, image_path: str) -> Tuple[str, float]:
        """
        Extract text from an image.
        Returns:
            Tuple[str, float]: The extracted text and the overall confidence score (0.0 to 1.0).
        """
        pass

class MockOCRAngine(OCRAngine):
    def extract_text(self, image_path: str) -> Tuple[str, float]:
        """
        Simulates OCR text extraction with a random choice from standard mock prescription layouts.
        """
        mock_texts = [
            "Rx\nTab Crocin 650\n1-0-1\n5 Days\n\nTab Amoxicillin 500\n1-1-1\n7 Days\n\nSyp Benadryl\n0-0-1\n3 Days",
            "Rx\nTab Dolo 650\n1-0-1\n3 Days\n\nCap Amoxicillin 500\n1-0-1\n5 Days",
            "Rx\nTab Atorvastatin 10\n0-0-1\n30 Days\n\nTab Metformin 500\n1-0-1\n15 Days",
            "Rx\nTab Combiflam\n1-0-1\n5 Days\n\nSyp Benadryl\n0-0-1\n10 Days"
        ]
        text = random.choice(mock_texts)
        confidence = round(random.uniform(0.88, 0.97), 2)
        return text, confidence

# Service Factory to resolve OCR engine (can read config or fallback to Mock)
def get_ocr_engine() -> OCRAngine:
    # Here you can check config parameters: e.g., settings.OCR_PROVIDER
    # If not set or equals "mock", return MockOCRAngine.
    return MockOCRAngine()
