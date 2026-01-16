"""Test script for PDF parser functionality.

This script tests the PDF parser with various scenarios:
- Sample PDF with text
- Multi-page documents
- PDFs with tables
- Error handling
"""

import sys
from pathlib import Path
import json

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from ingestion.parsers import parse_pdf, parse_document


def create_sample_pdf():
    """Create a sample PDF for testing using reportlab."""
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib import colors
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
        from reportlab.lib.styles import getSampleStyleSheet
    except ImportError:
        print("⚠️  reportlab not installed. Install with: pip install reportlab")
        return None

    sample_pdf_path = Path(__file__).parent / "sample_test.pdf"

    doc = SimpleDocTemplate(str(sample_pdf_path), pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # Page 1: Introduction
    story.append(Paragraph("Sample PDF Document for Testing", styles['Title']))
    story.append(Spacer(1, 12))
    story.append(Paragraph("Introduction", styles['Heading1']))
    story.append(Spacer(1, 12))

    intro_text = """
    This is a sample PDF document created for testing the PDF parser functionality.
    It contains multiple pages with various types of content including text, tables,
    and different formatting styles. The parser should be able to extract all this
    information correctly.
    """
    story.append(Paragraph(intro_text, styles['Normal']))
    story.append(Spacer(1, 12))

    # Add a table
    story.append(Paragraph("Sample Table", styles['Heading2']))
    story.append(Spacer(1, 12))

    data = [
        ['Product', 'Quantity', 'Price', 'Total'],
        ['Widget A', '10', '$5.00', '$50.00'],
        ['Widget B', '5', '$12.00', '$60.00'],
        ['Widget C', '8', '$8.50', '$68.00'],
        ['Total', '', '', '$178.00']
    ]

    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(table)
    story.append(PageBreak())

    # Page 2: More content
    story.append(Paragraph("Page 2: Additional Information", styles['Heading1']))
    story.append(Spacer(1, 12))

    page2_text = """
    This is the second page of the document. Multi-page documents are common in
    real-world scenarios, and the parser needs to handle them properly. Each page
    should be processed sequentially, and the text should be extracted while
    maintaining the logical structure.

    Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod
    tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam,
    quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo
    consequat.
    """
    story.append(Paragraph(page2_text, styles['Normal']))
    story.append(Spacer(1, 12))

    # Another table
    story.append(Paragraph("Performance Metrics", styles['Heading2']))
    story.append(Spacer(1, 12))

    metrics = [
        ['Metric', 'Q1', 'Q2', 'Q3', 'Q4'],
        ['Revenue', '$1.2M', '$1.5M', '$1.8M', '$2.1M'],
        ['Users', '10,000', '15,000', '22,000', '30,000'],
        ['Satisfaction', '85%', '88%', '90%', '92%']
    ]

    metrics_table = Table(metrics)
    metrics_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.navy),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(metrics_table)

    # Build PDF
    doc.build(story)
    print(f"✅ Created sample PDF: {sample_pdf_path}")
    return sample_pdf_path


def test_pdf_parser(pdf_path: Path):
    """Test the PDF parser with a given PDF file."""
    print(f"\n{'='*60}")
    print(f"Testing PDF Parser with: {pdf_path.name}")
    print(f"{'='*60}\n")

    try:
        # Parse the PDF
        result = parse_pdf(pdf_path)

        # Display results
        print(f"Status: {result['status']}")
        print(f"\nMetadata:")
        print(f"  File: {result['metadata'].get('file_name', 'N/A')}")
        print(f"  Pages: {result['metadata'].get('num_pages', 0)}")
        print(f"  Size: {result['metadata'].get('file_size', 0):,} bytes")
        print(f"  Title: {result['metadata'].get('title', 'N/A')}")
        print(f"  Author: {result['metadata'].get('author', 'N/A')}")

        print(f"\nExtracted Text (first 500 chars):")
        print("-" * 60)
        print(result['text'][:500])
        if len(result['text']) > 500:
            print(f"... ({len(result['text']) - 500} more characters)")
        print("-" * 60)

        print(f"\nPages Processed: {len(result['pages'])}")
        for page in result['pages'][:3]:  # Show first 3 pages
            print(f"  Page {page['page_number']}: {page['char_count']} characters")

        print(f"\nTables Extracted: {len(result['tables'])}")
        for table in result['tables']:
            print(f"  Page {table['page_number']}, Table {table['table_index']}: "
                  f"{table['rows']} rows × {table['columns']} columns")
            # Show first few rows of each table
            if table['data']:
                print(f"    Sample data:")
                for row in table['data'][:3]:
                    print(f"      {row}")

        if result['errors']:
            print(f"\nErrors/Warnings:")
            for error in result['errors']:
                print(f"  ⚠️  {error}")

        print(f"\n✅ PDF parsing completed successfully!")
        return True

    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_parse_document_routing():
    """Test the parse_document routing function."""
    print(f"\n{'='*60}")
    print(f"Testing parse_document() routing")
    print(f"{'='*60}\n")

    sample_pdf = Path(__file__).parent / "sample_test.pdf"

    if not sample_pdf.exists():
        print("⚠️  Sample PDF not found, skipping routing test")
        return False

    try:
        result = parse_document(sample_pdf)
        print(f"✅ Routing successful! Parsed {result['metadata'].get('num_pages', 0)} pages")
        return True
    except Exception as e:
        print(f"❌ Routing failed: {e}")
        return False


def test_error_handling():
    """Test error handling with non-existent and invalid files."""
    print(f"\n{'='*60}")
    print(f"Testing Error Handling")
    print(f"{'='*60}\n")

    # Test 1: Non-existent file
    print("Test 1: Non-existent file")
    try:
        parse_pdf(Path("nonexistent.pdf"))
        print("❌ Should have raised FileNotFoundError")
        return False
    except FileNotFoundError:
        print("✅ Correctly raised FileNotFoundError")

    # Test 2: Invalid file (not a PDF)
    print("\nTest 2: Invalid file format")
    invalid_file = Path(__file__).parent / "test_invalid.txt"
    try:
        with open(invalid_file, 'w') as f:
            f.write("This is not a PDF file")

        result = parse_pdf(invalid_file)
        if result['status'] == 'error':
            print("✅ Correctly handled invalid PDF")
        else:
            print("⚠️  Invalid PDF didn't produce error status")

        invalid_file.unlink()  # Clean up
    except Exception as e:
        print(f"⚠️  Error handling test: {e}")
        if invalid_file.exists():
            invalid_file.unlink()

    return True


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("PDF Parser Test Suite")
    print("="*60)

    # Create sample PDF
    sample_pdf = create_sample_pdf()

    if sample_pdf is None:
        print("\n⚠️  Could not create sample PDF. Trying to find existing PDF files...")
        # Look for any PDF in the current directory
        pdf_files = list(Path(__file__).parent.glob("*.pdf"))
        if pdf_files:
            sample_pdf = pdf_files[0]
            print(f"Found PDF: {sample_pdf}")
        else:
            print("❌ No PDF files found. Cannot run tests.")
            print("   Install reportlab (pip install reportlab) to create a sample PDF")
            return

    # Run tests
    tests_passed = 0
    tests_total = 3

    if test_pdf_parser(sample_pdf):
        tests_passed += 1

    if test_parse_document_routing():
        tests_passed += 1

    if test_error_handling():
        tests_passed += 1

    # Summary
    print(f"\n{'='*60}")
    print(f"Test Summary: {tests_passed}/{tests_total} tests passed")
    print(f"{'='*60}\n")

    if tests_passed == tests_total:
        print("✅ All tests passed!")
    else:
        print(f"⚠️  {tests_total - tests_passed} test(s) failed")


if __name__ == "__main__":
    main()
