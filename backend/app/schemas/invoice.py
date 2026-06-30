from pydantic import BaseModel, Field
from typing import List, Optional, Any
from datetime import datetime


class InvoiceItem(BaseModel):
    name: str = ""
    quantity: str = ""
    unit_price: str = ""
    total: str = ""


class StructuredInvoice(BaseModel):
    vendor: str = ""
    invoice_number: str = ""
    invoice_date: str = ""
    items: List[InvoiceItem] = Field(default_factory=list)
    subtotal: str = ""
    tax: str = ""
    grand_total: str = ""
    payment_method: str = ""


class ProcessingLog(BaseModel):
    id: int
    invoice_id: int
    stage: str
    message: str
    duration_ms: float
    created_at: datetime

    class Config:
        from_attributes = True


class InvoiceResponse(BaseModel):
    id: int
    filename: str
    original_text: Optional[str] = None
    structured_json: Optional[Any] = None
    processing_time_ms: Optional[float] = None
    cpu_usage: Optional[float] = None
    memory_usage: Optional[float] = None
    model_used: Optional[str] = None
    status: str
    error_message: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    logs: Optional[List[ProcessingLog]] = None

    class Config:
        from_attributes = True


class InvoiceListResponse(BaseModel):
    total: int
    invoices: List[InvoiceResponse]


class DashboardResponse(BaseModel):
    total_invoices: int
    pending: int
    processing: int
    completed: int
    failed: int
    latest_invoices: List[InvoiceResponse]


class HealthResponse(BaseModel):
    status: str
    version: str
    model_loaded: bool
    model_path: Optional[str] = None
    ocr_available: bool
    uptime: float
    config: dict


class UploadResponse(BaseModel):
    id: int
    filename: str
    status: str
    message: str
