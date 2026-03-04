from __future__ import annotations

from pathlib import Path


class OCRExtractor:
    def extract_pdf(self, file_path: str | Path) -> str:
        try:
            import pdfplumber
            import pytesseract
        except ImportError as exc:  # pragma: no cover - dependency guard
            raise RuntimeError("pdfplumber and pytesseract are required for OCR extraction") from exc

        text_chunks: list[str] = []
        with pdfplumber.open(str(file_path)) as pdf:
            for page in pdf.pages:
                pil_image = page.to_image(resolution=300).original.convert("RGB")
                text_chunks.append(pytesseract.image_to_string(pil_image))
        return "\n".join(chunk for chunk in text_chunks if chunk).strip()

    def extract_image(self, file_path: str | Path) -> str:
        try:
            from PIL import Image
            import pytesseract
        except ImportError as exc:  # pragma: no cover - dependency guard
            raise RuntimeError("Pillow and pytesseract are required for image OCR") from exc

        image = Image.open(file_path)
        return pytesseract.image_to_string(image)
