import re
import json
import time
import logging
import psutil
from pathlib import Path
from typing import Optional, Tuple, Any

logger = logging.getLogger(__name__)


def sanitize_filename(filename: str) -> str:
    name = re.sub(r'[^\w\s.-]', '', filename)
    name = re.sub(r'\s+', '_', name)
    return name


def extract_extension(filename: str) -> str:
    return Path(filename).suffix.lower()


def is_allowed_file(filename: str, allowed_extensions: list) -> bool:
    return extract_extension(filename) in allowed_extensions


def get_file_size_mb(file_path: Path) -> float:
    return file_path.stat().st_size / (1024 * 1024)


def parse_json_safely(text: str) -> Optional[dict]:
    text = text.strip()
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


def extract_json_from_text(text: str) -> Optional[dict]:
    result = parse_json_safely(text)
    if result:
        return result
    brace_count = 0
    start = -1
    for i, ch in enumerate(text):
        if ch == '{':
            if brace_count == 0:
                start = i
            brace_count += 1
        elif ch == '}':
            brace_count -= 1
            if brace_count == 0 and start >= 0:
                candidate = text[start:i + 1]
                result = parse_json_safely(candidate)
                if result:
                    return result
                start = -1
    return None


def get_system_stats() -> Tuple[float, float]:
    try:
        cpu = psutil.cpu_percent(interval=0.1)
        mem = psutil.virtual_memory().percent
        return cpu, mem
    except Exception:
        return 0.0, 0.0


def format_duration(seconds: float) -> str:
    if seconds < 1:
        return f"{seconds * 1000:.0f}ms"
    if seconds < 60:
        return f"{seconds:.1f}s"
    return f"{seconds / 60:.1f}m"


class Timer:
    def __init__(self):
        self.start: float = 0.0
        self.elapsed: float = 0.0

    def __enter__(self):
        self.start = time.perf_counter()
        return self

    def __exit__(self, *args):
        self.elapsed = time.perf_counter() - self.start

    def get_ms(self) -> float:
        return self.elapsed * 1000
