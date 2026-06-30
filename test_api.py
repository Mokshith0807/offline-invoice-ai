"""
Testing script for the Offline Invoice Structurer AI.
Run: python test_api.py
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "backend"))

import requests

BASE = "http://localhost:8000"


def test_health():
    r = requests.get(f"{BASE}/api/health")
    assert r.status_code == 200
    data = r.json()
    print(f"[PASS] Health: {data['status']} (model={data['model_loaded']}, ocr={data['ocr_available']})")
    return data


def test_upload_no_file():
    r = requests.post(f"{BASE}/api/upload")
    assert r.status_code == 422
    print("[PASS] Upload without file returns 422")


def test_upload_dummy():
    r = requests.post(
        f"{BASE}/api/upload",
        files={"file": ("test.txt", b"hello", "text/plain")},
    )
    assert r.status_code == 400
    print(f"[PASS] Invalid file type rejected: {r.json()['detail']}")


def test_dashboard():
    r = requests.get(f"{BASE}/api/dashboard")
    assert r.status_code == 200
    data = r.json()
    print(f"[PASS] Dashboard: {data['total_invoices']} invoices")


def test_invoices_empty():
    r = requests.get(f"{BASE}/api/invoices")
    assert r.status_code == 200
    data = r.json()
    print(f"[PASS] Invoices list: {data['total']} total")


def test_invoice_not_found():
    r = requests.get(f"{BASE}/api/invoice/99999")
    assert r.status_code == 404
    print("[PASS] Non-existent invoice returns 404")


def test_delete_not_found():
    r = requests.delete(f"{BASE}/api/invoice/99999")
    assert r.status_code == 404
    print("[PASS] Delete non-existent returns 404")


def test_all():
    tests = [
        test_health,
        test_upload_no_file,
        test_upload_dummy,
        test_dashboard,
        test_invoices_empty,
        test_invoice_not_found,
        test_delete_not_found,
    ]
    passed = 0
    failed = 0
    for t in tests:
        try:
            t()
            passed += 1
        except Exception as e:
            print(f"[FAIL] {t.__name__}: {e}")
            failed += 1

    print(f"\n{'=' * 40}")
    print(f"Results: {passed} passed, {failed} failed")
    return failed == 0


if __name__ == "__main__":
    success = test_all()
    sys.exit(0 if success else 1)
