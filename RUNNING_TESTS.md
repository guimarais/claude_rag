unning the PDF Parser Tests

  Quick Method (Recommended)

  .venv/bin/python backend/ingestion/test_pdf_parser.py

  Alternative (if venv is activated)

  source .venv/bin/activate
  python backend/ingestion/test_pdf_parser.py

  What the Test Does

  The test script will:
  1. Create a sample PDF with 2 pages and 2 tables (using reportlab)
  2. Test text extraction from multi-page documents
  3. Test table extraction with pdfplumber
  4. Test metadata extraction (file info, PDF properties)
  5. Test the routing function (parse_document())
  6. Test error handling (non-existent files, corrupted PDFs)

  Expected Output

  You should see:
  - ✅ All 3 tests passed
  - Extracted text preview
  - Table structure information
  - Metadata details
  - Per-page statistics

  Dependencies Note

  The test currently works because we installed the minimal dependencies:
  - pypdf (text extraction)
  - pdfplumber (table extraction)
  - reportlab (PDF creation for testing)
