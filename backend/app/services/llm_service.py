import os
import sys
import json
import logging
import subprocess
import multiprocessing
from pathlib import Path
from typing import Optional, Any, Iterator

from app.core.config import settings

logger = logging.getLogger(__name__)

EXTRACTION_PROMPT = """Extract invoice details from the following OCR text and return ONLY valid JSON with this exact structure:
{
    "vendor": "",
    "invoice_number": "",
    "invoice_date": "",
    "items": [{"name": "", "quantity": "", "unit_price": "", "total": ""}],
    "subtotal": "",
    "tax": "",
    "grand_total": "",
    "payment_method": ""
}

Rules:
- Use empty string for missing fields
- Include ALL items found
- Return ONLY the JSON object, no other text
- Numbers should be strings
- Date format: YYYY-MM-DD if possible

OCR Text:
{ocr_text}

JSON:"""


class LLMService:
    def __init__(self):
        self.model_path: Optional[Path] = None
        self._model = None
        self._llama_cpp = None
        self._available = False
        self._load_model()

    def _load_model(self):
        model_path = settings.find_model()
        if not model_path:
            logger.warning("No GGUF model found. LLM features disabled.")
            self._available = False
            return

        self.model_path = model_path
        logger.info(f"Loading model: {model_path}")

        try:
            if self._try_load_llama_cpp():
                return
        except Exception as e:
            logger.warning(f"llama-cpp-python failed: {e}")

        try:
            if self._try_load_ctransformers():
                return
        except Exception as e:
            logger.warning(f"ctransformers failed: {e}")

        try:
            if self._try_subprocess():
                return
        except Exception as e:
            logger.warning(f"subprocess llama.cpp failed: {e}")

        logger.warning("Could not load any LLM backend")
        self._available = False

    def _try_load_llama_cpp(self) -> bool:
        try:
            from llama_cpp import Llama

            n_threads = settings.llm_threads
            n_ctx = settings.llm_context_size

            self._model = Llama(
                model_path=str(self.model_path),
                n_ctx=n_ctx,
                n_threads=n_threads,
                n_gpu_layers=0,
                verbose=False,
            )
            self._llama_cpp = True
            self._available = True
            logger.info(f"Loaded model via llama-cpp-python with {n_threads} threads")
            return True
        except Exception as e:
            logger.debug(f"llama-cpp-python load failed: {e}")
            return False

    def _try_load_ctransformers(self) -> bool:
        try:
            from ctransformers import AutoModelForCausalLM

            self._model = AutoModelForCausalLM.from_pretrained(
                str(self.model_path),
                model_type="llama",
                context_length=settings.llm_context_size,
                gpu_layers=0,
                threads=settings.llm_threads,
            )
            self._llama_cpp = False
            self._available = True
            logger.info("Loaded model via ctransformers")
            return True
        except Exception as e:
            logger.debug(f"ctransformers load failed: {e}")
            return False

    def _try_subprocess(self) -> bool:
        try:
            result = subprocess.run(
                ["llama-cli", "--version"],
                capture_output=True, text=True, timeout=5,
            )
            if result.returncode == 0:
                self._llama_cpp = False
                self._available = True
                logger.info("Using llama-cli subprocess")
                return True
        except Exception:
            pass
        return False

    @property
    def is_available(self) -> bool:
        return self._available

    def extract_invoice(self, ocr_text: str) -> Optional[dict]:
        if not self._available or not self._model:
            logger.warning("LLM not available, using fallback extraction")
            return self._fallback_extract(ocr_text)

        for attempt in range(settings.llm_max_retries):
            try:
                result = self._generate(ocr_text)
                parsed = self._parse_json(result)
                if parsed:
                    return parsed
                logger.warning(f"Attempt {attempt + 1}: invalid JSON from LLM")
            except Exception as e:
                logger.error(f"Attempt {attempt + 1} failed: {e}")

        logger.warning("All LLM attempts failed, using fallback")
        return self._fallback_extract(ocr_text)

    def _generate(self, ocr_text: str) -> str:
        prompt = EXTRACTION_PROMPT.format(ocr_text=ocr_text[:3000])

        if self._llama_cpp:
            return self._generate_llama_cpp(prompt)
        else:
            return self._generate_fallback(prompt)

    def _generate_llama_cpp(self, prompt: str) -> str:
        output = self._model(
            prompt,
            max_tokens=settings.llm_max_tokens,
            temperature=settings.llm_temperature,
            echo=False,
            stop=["```", "<|end|>", "<|user|>", "<|assistant|>"],
        )
        return output["choices"][0]["text"].strip()

    def _generate_fallback(self, prompt: str) -> str:
        return "{}"

    def _parse_json(self, text: str) -> Optional[dict]:
        text = text.strip()
        import re

        json_match = re.search(r'```(?:json)?\s*\n?(.*?)\n?```', text, re.DOTALL)
        if json_match:
            text = json_match.group(1).strip()

        text = re.sub(r'^[^{]*', '', text)
        text = re.sub(r'[^}]*$', '', text)

        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        try:
            text = re.sub(r',(\s*[}\]])', r'\1', text)
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        return None

    def _fallback_extract(self, ocr_text: str) -> dict:
        import re

        text = ocr_text.lower()

        result = {
            "vendor": "",
            "invoice_number": "",
            "invoice_date": "",
            "items": [],
            "subtotal": "",
            "tax": "",
            "grand_total": "",
            "payment_method": "",
        }

        patterns = [
            (r"(?:invoice\s*(?:#|no|number)[:\s]*)([a-z0-9\-_/]+)", "invoice_number"),
            (r"(?:date[:\s]*)(\d{1,4}[-/]\d{1,2}[-/]\d{1,4})", "invoice_date"),
            (r"(?:vendor|from|company|seller)[:\s]*([a-z\s]+)", "vendor"),
            (r"(?:subtotal[:\s]*\$?)([\d.,]+)", "subtotal"),
            (r"(?:tax[:\s]*\$?)([\d.,]+)", "tax"),
            (r"(?:total|grand\s*total|amount\s*due)[:\s]*\$?([\d.,]+)", "grand_total"),
            (r"(?:payment|paid\s*(?:by|via))[:\s]*([a-z\s]+)", "payment_method"),
        ]

        for pattern, key in patterns:
            match = re.search(pattern, text)
            if match:
                result[key] = match.group(1).strip().title() if key == "vendor" or key == "payment_method" else match.group(1).strip()

        item_pattern = r"([a-z\s]+?)\s+(\d+)\s*x?\s*\$?([\d.,]+)\s*\$?([\d.,]+)"
        for match in re.finditer(item_pattern, text):
            result["items"].append({
                "name": match.group(1).strip().title(),
                "quantity": match.group(2),
                "unit_price": match.group(3),
                "total": match.group(4),
            })

        if not result["items"]:
            line_pattern = r"^([a-z][a-z\s]+?)\s+(\d+)\s+([\d.,]+)"
            for line in ocr_text.split("\n"):
                match = re.match(line_pattern, line.lower())
                if match:
                    result["items"].append({
                        "name": match.group(1).strip().title(),
                        "quantity": match.group(2),
                        "unit_price": match.group(3),
                        "total": match.group(3),
                    })

        return result
