import json
import csv
import io
import logging
import time
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from fastapi.responses import StreamingResponse, PlainTextResponse
from starlette.responses import JSONResponse

from app.core.config import settings
from app.services.ocr_service import OCRService
from app.services.llm_service import LLMService
from app.services.invoice_service import (
    InvoiceProcessor,
    get_invoice_from_db,
    get_all_invoices,
    delete_invoice,
    get_dashboard_data,
)
from app.utils.helpers import is_allowed_file, sanitize_filename

logger = logging.getLogger(__name__)

router = APIRouter()

ocr_service = OCRService()
llm_service = LLMService()
processor = InvoiceProcessor(ocr_service, llm_service)

_start_time = time.time()


@router.get("/health")
async def health():
    return {
        "status": "healthy",
        "version": settings.app_version,
        "model_loaded": llm_service.is_available,
        "model_path": str(llm_service.model_path) if llm_service.model_path else None,
        "ocr_available": ocr_service.is_available,
        "uptime": time.time() - _start_time,
        "config": settings.to_dict(),
    }


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    ext = Path(file.filename).suffix.lower()
    if not is_allowed_file(file.filename, settings.allowed_extensions):
        raise HTTPException(
            status_code=400,
            detail=f"File type '{ext}' not allowed. Allowed: {', '.join(settings.allowed_extensions)}",
        )

    safe_name = sanitize_filename(file.filename)
    file_path = settings.upload_dir / f"{int(time.time())}_{safe_name}"

    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Empty file")

    file_path.write_bytes(content)

    result = processor.process(file_path, file.filename, file_path_str=str(file_path))

    return JSONResponse(content={
        "id": result["id"],
        "filename": result["filename"],
        "status": result["status"],
        "message": "Processing completed" if result["status"] == "completed" else f"Processing failed: {result.get('error_message', 'Unknown error')}",
    })


@router.post("/process/{invoice_id}")
async def process_invoice(invoice_id: int):
    invoice = get_invoice_from_db(invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    file_path = None
    if invoice.get("file_path") and Path(invoice["file_path"]).exists():
        file_path = Path(invoice["file_path"])
    else:
        safe_name = sanitize_filename(invoice["filename"])
        for f in settings.upload_dir.iterdir():
            if safe_name in f.name:
                file_path = f
                break

    if not file_path or not file_path.exists():
        raise HTTPException(status_code=404, detail="Original file not found. Re-upload the file instead.")

    result = processor.process(file_path, invoice["filename"], file_path_str=str(file_path))
    return JSONResponse(content={
        "id": result["id"],
        "status": result["status"],
        "message": "Processing completed" if result["status"] == "completed" else f"Failed: {result.get('error_message', '')}",
    })


@router.get("/invoices")
async def list_invoices(
    search: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    data = get_all_invoices(search=search, limit=limit, offset=offset)
    return JSONResponse(content=data)


@router.get("/invoice/{invoice_id}")
async def get_invoice(invoice_id: int):
    invoice = get_invoice_from_db(invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return JSONResponse(content=invoice)


@router.delete("/invoice/{invoice_id}")
async def remove_invoice(invoice_id: int):
    deleted = delete_invoice(invoice_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return {"message": "Invoice deleted successfully"}


@router.get("/dashboard")
async def dashboard():
    data = get_dashboard_data()
    return JSONResponse(content=data)


@router.get("/invoice/{invoice_id}/export/json")
async def export_invoice_json(invoice_id: int):
    invoice = get_invoice_from_db(invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    if not invoice.get("structured_json"):
        raise HTTPException(status_code=404, detail="No structured data to export")

    content = json.dumps(invoice["structured_json"], indent=2)
    return StreamingResponse(
        io.BytesIO(content.encode()),
        media_type="application/json",
        headers={"Content-Disposition": f'attachment; filename="invoice_{invoice_id}.json"'},
    )


@router.get("/invoice/{invoice_id}/export/csv")
async def export_invoice_csv(invoice_id: int):
    invoice = get_invoice_from_db(invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    if not invoice.get("structured_json"):
        raise HTTPException(status_code=404, detail="No structured data to export")

    data = invoice["structured_json"]
    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(["Field", "Value"])
    writer.writerow(["Vendor", data.get("vendor", "")])
    writer.writerow(["Invoice Number", data.get("invoice_number", "")])
    writer.writerow(["Date", data.get("invoice_date", "")])
    writer.writerow(["Subtotal", data.get("subtotal", "")])
    writer.writerow(["Tax", data.get("tax", "")])
    writer.writerow(["Grand Total", data.get("grand_total", "")])
    writer.writerow(["Payment Method", data.get("payment_method", "")])
    writer.writerow([])

    if data.get("items"):
        writer.writerow(["Item", "Quantity", "Unit Price", "Total"])
        for item in data["items"]:
            writer.writerow([
                item.get("name", ""),
                item.get("quantity", ""),
                item.get("unit_price", ""),
                item.get("total", ""),
            ])

    content = output.getvalue()
    return StreamingResponse(
        io.BytesIO(content.encode()),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="invoice_{invoice_id}.csv"'},
    )


@router.get("/invoice/{invoice_id}/export/ocr")
async def export_invoice_ocr(invoice_id: int):
    invoice = get_invoice_from_db(invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    if not invoice.get("original_text"):
        raise HTTPException(status_code=404, detail="No OCR text available")

    return PlainTextResponse(
        content=invoice["original_text"],
        headers={"Content-Disposition": f'attachment; filename="invoice_{invoice_id}_ocr.txt"'},
    )
