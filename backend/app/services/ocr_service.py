import os
import asyncio
from abc import ABC, abstractmethod
from typing import Tuple
from PIL import Image

class OCRAngine(ABC):
    @abstractmethod
    def extract_text(self, image_path: str) -> Tuple[str, float]:
        """
        Extract text from an image.
        Returns:
            Tuple[str, float]: The extracted text and the overall confidence score (0.0 to 1.0).
        """
        pass

class RealOCRAngine(OCRAngine):
    def extract_text(self, image_path: str) -> Tuple[str, float]:
        """
        Extracts genuine text from image using native Windows Media OCR (winocr) with PIL.
        """
        if not image_path or not os.path.exists(image_path):
            return "", 0.0

        try:
            import winocr
            img = Image.open(image_path)
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

            if loop.is_running():
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                    res = pool.submit(asyncio.run, winocr.recognize_pil(img, 'en')).result()
            else:
                res = loop.run_until_complete(winocr.recognize_pil(img, 'en'))

            extracted = (res.text or "").strip()
            confidence = 0.94 if len(extracted) > 20 else 0.70
            return extracted, confidence
        except Exception:
            return "", 0.0

def get_ocr_engine() -> OCRAngine:
    return RealOCRAngine()
