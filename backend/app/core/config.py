import os
import json
import multiprocessing
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Settings:
    app_name: str = "Offline Invoice Structurer AI"
    app_version: str = "1.0.0"
    debug: bool = False

    base_dir: Path = Path(__file__).resolve().parent.parent.parent.parent
    upload_dir: Path = field(default_factory=lambda: Path(os.getenv("UPLOAD_DIR", "uploads")))
    database_dir: Path = field(default_factory=lambda: Path(os.getenv("DATABASE_DIR", "database")))
    models_dir: Path = field(default_factory=lambda: Path(os.getenv("MODELS_DIR", "models")))
    logs_dir: Path = field(default_factory=lambda: Path(os.getenv("LOGS_DIR", "logs")))

    database_url: str = field(default_factory=lambda: os.getenv("DATABASE_URL", "sqlite:///database/invoices.db"))

    max_upload_size_mb: int = 50
    allowed_extensions: list = field(default_factory=lambda: [".jpg", ".jpeg", ".png", ".pdf"])

    ocr_language: str = field(default_factory=lambda: os.getenv("OCR_LANGUAGE", "eng"))
    ocr_confidence_threshold: int = 30

    llm_model_path: Optional[str] = field(default_factory=lambda: os.getenv("LLM_MODEL_PATH"))
    llm_context_size: int = int(os.getenv("LLM_CONTEXT_SIZE", "2048"))
    llm_threads: int = int(os.getenv("LLM_THREADS", str(max(1, multiprocessing.cpu_count() - 1))))
    llm_max_tokens: int = int(os.getenv("LLM_MAX_TOKENS", "1024"))
    llm_temperature: float = float(os.getenv("LLM_TEMPERATURE", "0.1"))
    llm_max_retries: int = 3

    default_model_search_paths: list = field(default_factory=lambda: [
        "models/phi-3-mini-4k-instruct-q4.gguf",
        "models/Phi-3-mini-4k-instruct-q4.gguf",
        "models/smollm2-360m-instruct-q4_k_m.gguf",
        "models/SmolLM2-360M-Instruct-Q4_K_M.gguf",
        "models/gemma-3-1b-it-q4_k_m.gguf",
        "models/tinyllama-1.1b-chat-v1.0-q4_k_m.gguf",
        "models/TinyLlama-1.1B-Chat-v1.0-Q4_K_M.gguf",
    ])

    cors_origins: list = field(default_factory=lambda: ["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173", "http://127.0.0.1:3000"])

    def __post_init__(self):
        self.upload_dir = self._resolve(self.upload_dir)
        self.database_dir = self._resolve(self.database_dir)
        self.models_dir = self._resolve(self.models_dir)
        self.logs_dir = self._resolve(self.logs_dir)

    def _resolve(self, p: Path) -> Path:
        if not p.is_absolute():
            return self.base_dir / p
        return p

    def ensure_dirs(self):
        for d in [self.upload_dir, self.database_dir, self.models_dir, self.logs_dir]:
            d.mkdir(parents=True, exist_ok=True)

    def find_model(self) -> Optional[Path]:
        if self.llm_model_path and Path(self.llm_model_path).exists():
            return Path(self.llm_model_path)
        for path_str in self.default_model_search_paths:
            p = self._resolve(Path(path_str))
            if p.exists():
                return p
            alt = self.models_dir / p.name
            if alt.exists():
                return alt
        return None

    def to_dict(self) -> dict:
        return {
            "app_name": self.app_name,
            "app_version": self.app_version,
            "debug": self.debug,
            "upload_dir": str(self.upload_dir),
            "database_dir": str(self.database_dir),
            "models_dir": str(self.models_dir),
            "llm_context_size": self.llm_context_size,
            "llm_threads": self.llm_threads,
            "llm_max_tokens": self.llm_max_tokens,
            "llm_temperature": self.llm_temperature,
            "ocr_language": self.ocr_language,
            "max_upload_size_mb": self.max_upload_size_mb,
        }


settings = Settings()
