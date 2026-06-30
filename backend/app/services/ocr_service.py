import logging
from pathlib import Path
from typing import List

from app.core.config import settings

logger = logging.getLogger(__name__)


class OCRService:
    def __init__(self):
        self._available = False
        self._check_availability()

    def _check_availability(self):
        try:
            import pytesseract
            pytesseract.get_tesseract_version()
            self._available = True
            logger.info("Tesseract OCR is available")
        except Exception as e:
            self._available = False
            logger.warning(f"Tesseract OCR not available: {e}")

    @property
    def is_available(self) -> bool:
        return self._available

    def extract_text(self, file_path: Path) -> str:
        ext = file_path.suffix.lower()
        if ext == ".pdf":
            return self._extract_from_pdf(file_path)
        return self._extract_from_image(file_path)

    def _extract_from_image(self, image_path: Path) -> str:
        from PIL import Image, ImageEnhance, ImageFilter, ImageOps

        img = Image.open(str(image_path))

        if img.size[0] < 300 and img.size[1] < 300:
            scale = max(600 / img.size[0], 600 / img.size[1])
            img = img.resize((int(img.size[0] * scale), int(img.size[1] * scale)), Image.LANCZOS)

        if img.mode == "RGBA":
            bg = Image.new("RGB", img.size, (255, 255, 255))
            bg.paste(img, mask=img.split()[3])
            img = bg

        gray = img.convert("L") if img.mode != "L" else img

        strategies = [
            ("contrast_sharpen", self._preprocess_contrast_sharpen),
            ("grayscale_raw", lambda x: x),
            ("otsu_binary", self._preprocess_otsu),
            ("inverted", lambda x: ImageOps.invert(x) if x.mode == "L" else x),
        ]

        psm_modes = [6, 4, 3]

        for psm in psm_modes:
            for name, preprocess in strategies:
                try:
                    processed = preprocess(gray)
                    text = self._run_tesseract(processed, psm)
                    if text.strip():
                        return self._clean_text(text)
                except Exception as e:
                    logger.debug(f"Strategy {name} PSM {psm} failed: {e}")

        return ""

    def _preprocess_contrast_sharpen(self, img):
        from PIL import Image, ImageEnhance, ImageFilter

        enhanced = ImageEnhance.Contrast(img).enhance(1.8)
        sharpened = enhanced.filter(ImageFilter.SHARPEN)
        return sharpened

    def _preprocess_otsu(self, img):

        w, h = img.size
        pixels = list(img.getdata())
        total = w * h

        hist = [0] * 256
        for p in pixels:
            hist[p] += 1

        sum_total = sum(i * hist[i] for i in range(256))
        sum_bg = 0
        w_bg = 0
        w_fg = 0

        max_var = 0
        threshold = 128

        for t in range(256):
            w_bg += hist[t]
            if w_bg == 0:
                continue
            w_fg = total - w_bg
            if w_fg == 0:
                break
            sum_bg += t * hist[t]
            mean_bg = sum_bg / w_bg
            mean_fg = (sum_total - sum_bg) / w_fg
            var = w_bg * w_fg * (mean_bg - mean_fg) ** 2
            if var > max_var:
                max_var = var
                threshold = t

        return img.point(lambda x: 255 if x > threshold else 0)

    def _run_tesseract(self, img, psm: int) -> str:
        import pytesseract
        config = f"--oem 3 --psm {psm} -l {settings.ocr_language}"
        return pytesseract.image_to_string(img, config=config)

    def _extract_from_pdf(self, pdf_path: Path) -> str:
        from pdf2image import convert_from_path

        images = convert_from_path(
            str(pdf_path),
            dpi=300,
            fmt="jpeg",
            thread_count=settings.llm_threads,
        )

        all_text = []
        for i, img in enumerate(images):
            temp_path = Path(f"{pdf_path}_page_{i}.png")
            try:
                img.save(str(temp_path), "PNG")
                text = self._extract_from_image(temp_path)
                if text.strip():
                    all_text.append(f"--- Page {i + 1} ---\n{text}")
            finally:
                if temp_path.exists():
                    temp_path.unlink()

        return "\n\n".join(all_text)

    def _clean_text(self, text: str) -> str:
        lines = []
        for line in text.split("\n"):
            line = line.strip()
            if line:
                lines.append(line)
        return "\n".join(lines)

    def get_available_languages(self) -> List[str]:
        import pytesseract
        try:
            return pytesseract.get_languages()
        except Exception:
            return ["eng"]
