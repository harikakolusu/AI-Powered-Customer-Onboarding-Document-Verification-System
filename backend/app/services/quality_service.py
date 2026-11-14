from pathlib import Path
from typing import Tuple, Dict, Any
import cv2
import numpy as np
from PIL import Image
from backend.app.config import BLUR_THRESHOLD, MIN_IMAGE_WIDTH, MIN_IMAGE_HEIGHT

class QualityService:
    @staticmethod
    def evaluate_image_quality(image_path: str | Path) -> Dict[str, Any]:
        """
        Assesses document image quality using Laplacian variance for blur detection
        and spatial resolution thresholds.
        """
        path = Path(image_path)
        path_str = str(path)

        # Handle PDF documents natively
        if path.suffix.lower() == ".pdf":
            try:
                import pypdf
                reader = pypdf.PdfReader(path_str)
                text_len = sum(len(p.extract_text() or "") for p in reader.pages)
                return {
                    "is_clear": True,
                    "quality_score": 150.0,
                    "quality_notes": f"Digital PDF Document ({len(reader.pages)} page(s), {text_len} characters extracted). High clarity.",
                    "width": 1000,
                    "height": 1400
                }
            except Exception as e:
                return {
                    "is_clear": False,
                    "quality_score": 0.0,
                    "quality_notes": f"Could not parse PDF: {str(e)}",
                    "width": 0,
                    "height": 0
                }

        img = cv2.imread(path_str)
        if img is None:
            # Attempt opening with PIL and convert to CV2 format
            try:
                pil_img = Image.open(path_str).convert("RGB")
                img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
            except Exception as e:
                return {
                    "is_clear": False,
                    "quality_score": 0.0,
                    "quality_notes": f"Could not read image: {str(e)}",
                    "width": 0,
                    "height": 0
                }

        height, width = img.shape[:2]
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Laplacian variance: higher = sharper, lower = blurry
        laplacian_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())

        issues = []
        is_clear = True

        if laplacian_var < BLUR_THRESHOLD:
            is_clear = False
            issues.append(f"Image is blurry (Sharpness index: {laplacian_var:.1f}, required: >= {BLUR_THRESHOLD:.1f})")

        if width < MIN_IMAGE_WIDTH or height < MIN_IMAGE_HEIGHT:
            is_clear = False
            issues.append(f"Low resolution: {width}x{height} (minimum required: {MIN_IMAGE_WIDTH}x{MIN_IMAGE_HEIGHT})")

        notes = "; ".join(issues) if issues else "Image is sharp and clear."

        return {
            "is_clear": is_clear,
            "quality_score": round(laplacian_var, 2),
            "quality_notes": notes,
            "width": width,
            "height": height
        }

