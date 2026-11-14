from pathlib import Path
from typing import Dict, Any, Optional
import json
import re
from PIL import Image

class OCRService:
    @staticmethod
    def extract_text_from_image(image_path: str | Path) -> str:
        """
        Attempts text extraction from an image or PDF using available tools.
        """
        path = Path(image_path)
        if not path.exists():
            return ""

        # Extract native text if file is PDF
        if path.suffix.lower() == ".pdf":
            try:
                import pypdf
                reader = pypdf.PdfReader(str(path))
                pages_text = [p.extract_text() or "" for p in reader.pages]
                return "\n".join(pages_text)
            except Exception:
                pass

        # Check if pytesseract or easyocr is available
        try:
            import pytesseract
            img = Image.open(path)
            return pytesseract.image_to_string(img)
        except Exception:
            pass

        return f"[Image OCR Source: {path.name}]"

