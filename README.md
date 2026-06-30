# Offline Invoice Structurer AI

A production-quality desktop/web application that converts invoice/receipt images or PDFs into structured JSON, **completely offline**. No cloud APIs. No internet required.

## 🏆 Hackathon Feature Highlights

- ✅ **Offline-First** — Everything runs locally, zero internet dependency
- ✅ **CPU-First AI** — Local LLM inference via llama.cpp on CPU (no GPU needed)
- ✅ **OCR Pipeline** — Tesseract-based text extraction with image preprocessing
- ✅ **Local LLM** — Phi-3 Mini / SmolLM2 / TinyLlama GGUF models
- ✅ **Full CRUD** — Upload, process, view, search, export, delete invoices
- ✅ **Structured JSON** — AI-powered extraction into a normalized schema
- ✅ **Dark Mode UI** — Modern React + Tailwind CSS dashboard
- ✅ **Docker Support** — One-command deployment

## 📋 Schema

```json
{
  "vendor": "Acme Corp",
  "invoice_number": "INV-2024-001",
  "invoice_date": "2024-01-15",
  "items": [
    {
      "name": "Widget A",
      "quantity": "2",
      "unit_price": "25.00",
      "total": "50.00"
    }
  ],
  "subtotal": "425.00",
  "tax": "34.00",
  "grand_total": "459.00",
  "payment_method": "Credit Card"
}
```

## 🏗 Architecture

```
Image/PDF  →  OCR (Tesseract)  →  Clean Text  →  Local LLM  →  Structured JSON  →  SQLite  →  Dashboard
```

### Data Flow

1. **Upload**: User drops invoice image or PDF via drag-and-drop
2. **OCR**: Tesseract extracts text (grayscale → threshold → denoise)
3. **LLM**: Local model converts raw OCR text into structured JSON
4. **Storage**: Original OCR + structured JSON saved to SQLite
5. **Dashboard**: View, search, export, and manage invoices

## 🛠 Tech Stack

| Component | Technology |
|-----------|-----------|
| **Backend** | Python + FastAPI |
| **Frontend** | React + Vite + Tailwind CSS |
| **Database** | SQLite |
| **OCR** | Tesseract (pytesseract) + pdf2image |
| **Local LLM** | llama.cpp Python bindings (GGUF models) |
| **Container** | Docker + docker-compose |

## 📦 Installation

### Prerequisites

- Python 3.10+
- Node.js 18+
- Tesseract OCR
- Poppler (for PDF processing)

#### Installing Tesseract

```bash
# Ubuntu/Debian
sudo apt-get install tesseract-ocr tesseract-ocr-eng poppler-utils

# macOS
brew install tesseract poppler

# Windows (via chocolatey)
choco install tesseract poppler
```

### Model Download

Download a GGUF model and place it in the `models/` directory:

```bash
# Phi-3 Mini (recommended - 2GB)
wget -O models/phi-3-mini-4k-instruct-q4.gguf \
  https://huggingface.co/microsoft/Phi-3-mini-4k-instruct-gguf/resolve/main/Phi-3-mini-4k-instruct-q4.gguf

# SmolLM2 (lighter - 200MB)
wget -O models/smollm2-360m-instruct-q4_k_m.gguf \
  https://huggingface.co/HuggingFaceTB/SmolLM2-360M-Instruct-gguf/resolve/main/SmolLM2-360M-Instruct-Q4_K_M.gguf

# TinyLlama (1.1B - 700MB)
wget -O models/tinyllama-1.1b-chat-v1.0-q4_k_m.gguf \
  https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/tinyllama-1.1b-chat-v1.0-q4_k_m.gguf
```

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt

# Optional: Install llama-cpp-python for local LLM
pip install llama-cpp-python

# Run
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

### Using Docker

```bash
docker-compose up --build
```

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | System health & capabilities |
| POST | `/api/upload` | Upload and process invoice |
| POST | `/api/process/{id}` | Reprocess existing invoice |
| GET | `/api/invoices` | List all invoices (search, paginate) |
| GET | `/api/invoice/{id}` | Get single invoice details |
| DELETE | `/api/invoice/{id}` | Delete invoice |
| GET | `/api/dashboard` | Dashboard statistics |
| GET | `/api/invoice/{id}/export/json` | Export as JSON |
| GET | `/api/invoice/{id}/export/csv` | Export as CSV |
| GET | `/api/invoice/{id}/export/ocr` | Download OCR text |

## ⚡ CPU Optimization Notes

- **4-bit GGUF quantization** — Uses Q4_K_M models for best accuracy/speed balance
- **Context window**: 2048 tokens (reduces memory usage)
- **Threads**: Auto-detects CPU cores (`os.cpu_count() - 1`)
- **Streaming**: LLM generates token-by-token (when using llama-cpp-python)
- **Image preprocessing**: Grayscale conversion, contrast enhancement, adaptive thresholding — reduces OCR noise
- **No GPU required**: Everything runs on CPU

## 🚀 Usage

1. Start both backend and frontend
2. Open http://localhost:5173
3. Drop an invoice image or PDF onto the upload area
4. Wait for OCR + LLM processing
5. View structured JSON result
6. Search, export (JSON/CSV/OCR), or delete invoices

## 🧪 Testing

```bash
# Start the backend first, then:
python test_api.py       # Test all API endpoints
python test_sample.py    # Create sample invoice and test end-to-end
```

## 📁 Project Structure

```
offline-invoice-ai/
├── backend/
│   ├── app/
│   │   ├── api/          # FastAPI routes
│   │   ├── core/         # Configuration
│   │   ├── db/           # Database setup
│   │   ├── schemas/      # Pydantic models
│   │   ├── services/     # OCR, LLM, Invoice processing
│   │   └── utils/        # Helpers, logging
│   ├── main.py           # Entry point
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env
├── frontend/
│   ├── src/
│   │   ├── components/   # Reusable UI components
│   │   ├── pages/        # Route pages
│   │   ├── hooks/        # Custom React hooks
│   │   ├── services/     # API client
│   │   ├── types/        # TypeScript types
│   │   └── styles/       # CSS
│   ├── package.json
│   ├── Dockerfile
│   └── nginx.conf
├── models/               # Place GGUF models here
├── uploads/              # Uploaded files
├── database/             # SQLite database
├── docker-compose.yml
├── test_api.py
├── test_sample.py
└── README.md
```

## 🔒 Offline-First Explained

This application is built on the **Offline First** principle:

1. **No external API calls** — OCR runs locally via Tesseract, LLM runs locally via GGUF
2. **Local storage** — All data persists in SQLite on your machine
3. **Graceful degradation** — If no LLM model is found, fallback regex extraction still works
4. **No telemetry** — Zero data leaves your computer
5. **Works without internet** — Full functionality on air-gapped systems

## 📸 Screenshots

*Dashboard — Upload invoices, view stats, browse recent activity*
*(Add screenshot here)*

*Invoice Detail — View structured JSON, vendor info, items, and processing logs*
*(Add screenshot here)*

*Invoices List — Search and filter all processed invoices*
*(Add screenshot here)*

## 📄 License

MIT
