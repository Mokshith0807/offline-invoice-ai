import json
import logging
from pathlib import Path
from typing import Optional, List
from datetime import datetime

from app.core.config import settings
from app.db.database import get_db
from app.services.ocr_service import OCRService
from app.services.llm_service import LLMService
from app.utils.helpers import Timer, get_system_stats, sanitize_filename

logger = logging.getLogger(__name__)


class InvoiceProcessor:
    def __init__(self, ocr_service: OCRService, llm_service: LLMService):
        self.ocr = ocr_service
        self.llm = llm_service

    def process(self, file_path: Path, filename: str, file_path_str: str = "") -> dict:
        result = {
            "id": None,
            "filename": filename,
            "original_text": "",
            "structured_json": None,
            "processing_time_ms": 0.0,
            "cpu_usage": 0.0,
            "memory_usage": 0.0,
            "model_used": str(self.llm.model_path) if self.llm.model_path else "fallback",
            "status": "pending",
            "error_message": None,
            "logs": [],
        }

        invoice_id = self._create_invoice_record(filename, file_path_str or str(file_path))
        result["id"] = invoice_id

        try:
            ocr_timer = Timer()
            with ocr_timer:
                self._add_log(invoice_id, "ocr", "Starting OCR extraction...")
                ocr_text = self.ocr.extract_text(file_path)
                if not ocr_text.strip():
                    raise ValueError("No text could be extracted from the document")

            result["original_text"] = ocr_text
            ocr_time = ocr_timer.get_ms()
            self._add_log(invoice_id, "ocr", f"OCR completed in {ocr_time:.0f}ms", ocr_time)
            self._update_invoice(invoice_id, original_text=ocr_text)

            llm_timer = Timer()
            with llm_timer:
                self._add_log(invoice_id, "llm", "Extracting invoice data with LLM...")
                structured = self.llm.extract_invoice(ocr_text)

            llm_time = llm_timer.get_ms()
            result["structured_json"] = structured
            self._add_log(invoice_id, "llm", f"LLM extraction completed in {llm_time:.0f}ms", llm_time)

            cpu, mem = get_system_stats()
            total_time = ocr_time + llm_time
            result["processing_time_ms"] = total_time
            result["cpu_usage"] = cpu
            result["memory_usage"] = mem

            self._update_invoice(
                invoice_id,
                structured_json=json.dumps(structured, indent=2) if structured else "{}",
                processing_time_ms=total_time,
                cpu_usage=cpu,
                memory_usage=mem,
                model_used=result["model_used"],
                status="completed",
            )
            result["status"] = "completed"
            self._add_log(invoice_id, "complete", f"Processing completed in {total_time:.0f}ms", total_time)

        except Exception as e:
            error_msg = str(e)
            logger.error(f"Processing failed for {filename}: {error_msg}")
            result["status"] = "failed"
            result["error_message"] = error_msg
            self._update_invoice(invoice_id, status="failed", error_message=error_msg)
            self._add_log(invoice_id, "error", f"Processing failed: {error_msg}")

        return result

    def _create_invoice_record(self, filename: str, file_path: str = "") -> int:
        with get_db() as db:
            cursor = db.execute(
                "INSERT INTO invoices (filename, file_path, status) VALUES (?, ?, ?)",
                (filename, file_path, "processing"),
            )
            return cursor.lastrowid

    def _update_invoice(self, invoice_id: int, **kwargs):
        fields = []
        values = []
        for key, val in kwargs.items():
            fields.append(f"{key} = ?")
            values.append(val)
        values.append(invoice_id)
        with get_db() as db:
            db.execute(
                f"UPDATE invoices SET {', '.join(fields)}, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                values,
            )

    def _add_log(self, invoice_id: int, stage: str, message: str, duration_ms: float = 0):
        with get_db() as db:
            db.execute(
                "INSERT INTO processing_logs (invoice_id, stage, message, duration_ms) VALUES (?, ?, ?, ?)",
                (invoice_id, stage, message, duration_ms),
            )


def get_invoice_from_db(invoice_id: int) -> Optional[dict]:
    with get_db() as db:
        row = db.execute("SELECT * FROM invoices WHERE id = ?", (invoice_id,)).fetchone()
        if not row:
            return None
        invoice = dict(row)
        logs = db.execute(
            "SELECT * FROM processing_logs WHERE invoice_id = ? ORDER BY created_at ASC",
            (invoice_id,),
        ).fetchall()
        invoice["logs"] = [dict(log) for log in logs]
        if invoice.get("structured_json"):
            try:
                invoice["structured_json"] = json.loads(invoice["structured_json"])
            except (json.JSONDecodeError, TypeError):
                pass
        return invoice


def get_all_invoices(search: Optional[str] = None, limit: int = 50, offset: int = 0) -> dict:
    with get_db() as db:
        if search:
            rows = db.execute(
                """SELECT * FROM invoices
                   WHERE vendor LIKE ? OR invoice_number LIKE ? OR invoice_date LIKE ? OR filename LIKE ?
                   ORDER BY created_at DESC LIMIT ? OFFSET ?""",
                (f"%{search}%", f"%{search}%", f"%{search}%", f"%{search}%", limit, offset),
            ).fetchall()
            total = db.execute(
                """SELECT COUNT(*) FROM invoices
                   WHERE vendor LIKE ? OR invoice_number LIKE ? OR invoice_date LIKE ? OR filename LIKE ?""",
                (f"%{search}%", f"%{search}%", f"%{search}%", f"%{search}%"),
            ).fetchone()[0]
        else:
            rows = db.execute(
                "SELECT * FROM invoices ORDER BY created_at DESC LIMIT ? OFFSET ?",
                (limit, offset),
            ).fetchall()
            total = db.execute("SELECT COUNT(*) FROM invoices").fetchone()[0]

        invoices = []
        for row in rows:
            inv = dict(row)
            if inv.get("structured_json"):
                try:
                    inv["structured_json"] = json.loads(inv["structured_json"])
                except (json.JSONDecodeError, TypeError):
                    pass
            invoices.append(inv)

        return {"total": total, "invoices": invoices}


def delete_invoice(invoice_id: int) -> bool:
    with get_db() as db:
        cursor = db.execute("DELETE FROM invoices WHERE id = ?", (invoice_id,))
        return cursor.rowcount > 0


def get_dashboard_data() -> dict:
    with get_db() as db:
        total = db.execute("SELECT COUNT(*) FROM invoices").fetchone()[0]
        pending = db.execute("SELECT COUNT(*) FROM invoices WHERE status = 'pending'").fetchone()[0]
        processing = db.execute("SELECT COUNT(*) FROM invoices WHERE status = 'processing'").fetchone()[0]
        completed = db.execute("SELECT COUNT(*) FROM invoices WHERE status = 'completed'").fetchone()[0]
        failed = db.execute("SELECT COUNT(*) FROM invoices WHERE status = 'failed'").fetchone()[0]

        latest_rows = db.execute(
            "SELECT * FROM invoices ORDER BY created_at DESC LIMIT 10"
        ).fetchall()

        latest = []
        for row in latest_rows:
            inv = dict(row)
            if inv.get("structured_json"):
                try:
                    inv["structured_json"] = json.loads(inv["structured_json"])
                except (json.JSONDecodeError, TypeError):
                    pass
            latest.append(inv)

        return {
            "total_invoices": total,
            "pending": pending,
            "processing": processing,
            "completed": completed,
            "failed": failed,
            "latest_invoices": latest,
        }
