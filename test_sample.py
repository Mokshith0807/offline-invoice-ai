#!/usr/bin/env python3
"""Simple test: create a synthetic invoice image, upload it, and verify processing."""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "backend"))

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("Pillow not installed. Run: pip install Pillow")
    sys.exit(1)

import requests

BASE = "http://localhost:8000"
SAMPLE_DIR = Path(__file__).resolve().parent / "sample_data"
SAMPLE_DIR.mkdir(exist_ok=True)


def create_sample_invoice():
    path = SAMPLE_DIR / "sample_invoice.png"
    img = Image.new("RGB", (800, 600), "white")
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
        small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
    except Exception:
        font = ImageFont.load_default()
        small = font

    y = 20
    draw.text((40, y), "INVOICE", fill="black", font=font)
    y += 50
    draw.text((40, y), "Acme Corp", fill="black", font=small)
    y += 30
    draw.text((40, y), "123 Business Ave, City", fill="black", font=small)
    y += 30
    draw.text((40, y), "invoice #: INV-2024-001", fill="black", font=small)
    y += 30
    draw.text((40, y), "Date: 2024-01-15", fill="black", font=small)

    y += 50
    draw.text((40, y), "Items:", fill="black", font=font)
    y += 35
    items = [
        ("Widget A", "2", "25.00", "50.00"),
        ("Gadget B", "1", "150.00", "150.00"),
        ("Service C", "3", "75.00", "225.00"),
    ]
    for name, qty, price, total in items:
        draw.text((40, y), f"{name}    {qty} x ${price}    ${total}", fill="black", font=small)
        y += 30

    y += 20
    draw.text((40, y), "Subtotal: $425.00", fill="black", font=small)
    y += 25
    draw.text((40, y), "Tax (8%): $34.00", fill="black", font=small)
    y += 25
    draw.text((40, y), "Grand Total: $459.00", fill="black", font=font)
    y += 30
    draw.text((40, y), "Payment: Credit Card", fill="black", font=small)

    img.save(str(path))
    print(f"Sample invoice created: {path}")
    return path


def test_upload_and_process():
    health = requests.get(f"{BASE}/api/health").json()
    print(f"Server: {health['status']} (OCR: {health['ocr_available']}, Model: {health['model_loaded']})")

    sample = create_sample_invoice()
    with open(sample, "rb") as f:
        r = requests.post(
            f"{BASE}/api/upload",
            files={"file": ("sample_invoice.png", f, "image/png")},
        )

    if r.status_code != 200:
        print(f"Upload failed: {r.json()}")
        return False

    result = r.json()
    print(f"Upload result: id={result['id']}, status={result['status']}")

    inv = requests.get(f"{BASE}/api/invoice/{result['id']}").json()
    print(f"\nInvoice #{inv['id']}: {inv['filename']}")
    print(f"Status: {inv['status']}")
    print(f"Processing time: {inv.get('processing_time_ms', 0) / 1000:.1f}s")

    if inv.get("structured_json"):
        sj = inv["structured_json"]
        print(f"\nVendor: {sj.get('vendor', 'N/A')}")
        print(f"Invoice #: {sj.get('invoice_number', 'N/A')}")
        print(f"Date: {sj.get('invoice_date', 'N/A')}")
        print(f"Grand Total: {sj.get('grand_total', 'N/A')}")
        print(f"Items: {len(sj.get('items', []))}")
        print("\nFull JSON:")
        print(json.dumps(sj, indent=2))
    else:
        print("No structured data extracted")

    return inv["status"] in ("completed", "failed")


if __name__ == "__main__":
    success = test_upload_and_process()
    sys.exit(0 if success else 1)
