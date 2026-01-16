"""Multi-format document parsers.

This module provides parsers for various document formats:
- PDF (using pypdf and pdfplumber for tables)
- DOCX (using python-docx)
- PPTX (using python-pptx)
- TXT/MD (plain text and markdown)
- CSV/XLSX (using pandas)

Each parser extracts text content and metadata while preserving
document structure where possible.
"""

from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

import pypdf
import pdfplumber

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def parse_pdf(file_path: Path) -> Dict[str, Any]:
    """Parse PDF document and extract text with metadata.

    Uses pypdf for text extraction and pdfplumber for table extraction.
    Handles multi-page documents and corrupted PDFs gracefully.

    Args:
        file_path: Path to PDF file

    Returns:
        Dictionary with the following keys:
        - 'text': Extracted text content (str)
        - 'tables': List of tables as list of lists
        - 'metadata': Document metadata (dict)
        - 'pages': List of per-page content (list)
        - 'images': List of image references (list)
        - 'status': 'success' or 'partial' or 'error'
        - 'errors': List of any errors encountered

    Raises:
        FileNotFoundError: If the PDF file doesn't exist
        ValueError: If the file is not a valid PDF
    """
    if not file_path.exists():
        raise FileNotFoundError(f"PDF file not found: {file_path}")

    result = {
        'text': '',
        'tables': [],
        'metadata': {},
        'pages': [],
        'images': [],
        'status': 'success',
        'errors': []
    }

    try:
        # Extract metadata and text using pypdf
        logger.info(f"Parsing PDF: {file_path}")

        with open(file_path, 'rb') as file:
            try:
                pdf_reader = pypdf.PdfReader(file)

                # Check if PDF is encrypted
                if pdf_reader.is_encrypted:
                    try:
                        pdf_reader.decrypt('')
                    except Exception as e:
                        result['status'] = 'error'
                        result['errors'].append(f"PDF is encrypted and cannot be decrypted: {e}")
                        logger.error(f"Failed to decrypt PDF: {e}")
                        return result

                # Extract metadata
                metadata = pdf_reader.metadata
                if metadata:
                    result['metadata'] = {
                        'title': metadata.get('/Title', ''),
                        'author': metadata.get('/Author', ''),
                        'subject': metadata.get('/Subject', ''),
                        'creator': metadata.get('/Creator', ''),
                        'producer': metadata.get('/Producer', ''),
                        'creation_date': metadata.get('/CreationDate', ''),
                        'modification_date': metadata.get('/ModDate', ''),
                    }

                # Add file metadata
                result['metadata'].update({
                    'file_name': file_path.name,
                    'file_path': str(file_path),
                    'file_size': file_path.stat().st_size,
                    'num_pages': len(pdf_reader.pages),
                    'parsed_at': datetime.now().isoformat(),
                })

                # Extract text from each page
                all_text = []
                for page_num, page in enumerate(pdf_reader.pages, start=1):
                    try:
                        page_text = page.extract_text()
                        if page_text:
                            all_text.append(page_text)
                            result['pages'].append({
                                'page_number': page_num,
                                'text': page_text,
                                'char_count': len(page_text)
                            })
                        else:
                            logger.warning(f"No text extracted from page {page_num}")
                            result['pages'].append({
                                'page_number': page_num,
                                'text': '',
                                'char_count': 0
                            })
                    except Exception as e:
                        error_msg = f"Error extracting text from page {page_num}: {e}"
                        result['errors'].append(error_msg)
                        logger.error(error_msg)
                        result['status'] = 'partial'

                result['text'] = '\n\n'.join(all_text)

            except pypdf.errors.PdfReadError as e:
                result['status'] = 'error'
                result['errors'].append(f"PDF read error: {e}")
                logger.error(f"Failed to read PDF with pypdf: {e}")
                return result
            except Exception as e:
                result['status'] = 'error'
                result['errors'].append(f"Unexpected error with pypdf: {e}")
                logger.error(f"Unexpected error parsing PDF: {e}")
                return result

        # Extract tables using pdfplumber
        try:
            with pdfplumber.open(file_path) as pdf:
                for page_num, page in enumerate(pdf.pages, start=1):
                    try:
                        tables = page.extract_tables()
                        if tables:
                            for table_idx, table in enumerate(tables):
                                if table and len(table) > 0:
                                    result['tables'].append({
                                        'page_number': page_num,
                                        'table_index': table_idx,
                                        'data': table,
                                        'rows': len(table),
                                        'columns': len(table[0]) if table else 0
                                    })
                                    logger.info(f"Extracted table {table_idx} from page {page_num}")
                    except Exception as e:
                        error_msg = f"Error extracting tables from page {page_num}: {e}"
                        result['errors'].append(error_msg)
                        logger.warning(error_msg)
                        result['status'] = 'partial'

        except Exception as e:
            error_msg = f"Failed to extract tables with pdfplumber: {e}"
            result['errors'].append(error_msg)
            logger.warning(error_msg)
            result['status'] = 'partial'

        # Log summary
        logger.info(f"PDF parsing complete: {len(result['pages'])} pages, "
                   f"{len(result['tables'])} tables, "
                   f"{len(result['text'])} characters")

        return result

    except Exception as e:
        result['status'] = 'error'
        result['errors'].append(f"Critical error parsing PDF: {e}")
        logger.error(f"Critical error in parse_pdf: {e}")
        return result


def parse_docx(file_path: Path) -> Dict[str, Any]:
    """Parse DOCX document and extract text with metadata.

    Args:
        file_path: Path to DOCX file

    Returns:
        Dictionary with 'text', 'metadata', and 'images' keys
    """
    # TODO: Implement DOCX parsing with python-docx
    pass


def parse_pptx(file_path: Path) -> Dict[str, Any]:
    """Parse PPTX presentation and extract text with metadata.

    Args:
        file_path: Path to PPTX file

    Returns:
        Dictionary with 'text', 'metadata', and 'images' keys
    """
    # TODO: Implement PPTX parsing with python-pptx
    pass


def parse_text(file_path: Path) -> Dict[str, Any]:
    """Parse plain text or markdown file.

    Args:
        file_path: Path to TXT or MD file

    Returns:
        Dictionary with 'text' and 'metadata' keys
    """
    # TODO: Implement text/markdown parsing
    pass


def parse_spreadsheet(file_path: Path) -> Dict[str, Any]:
    """Parse CSV or XLSX spreadsheet.

    Args:
        file_path: Path to CSV or XLSX file

    Returns:
        Dictionary with 'text' (formatted data) and 'metadata' keys
    """
    # TODO: Implement spreadsheet parsing with pandas
    pass


def parse_document(file_path: Path) -> Dict[str, Any]:
    """Route document to appropriate parser based on file extension.

    Args:
        file_path: Path to document file

    Returns:
        Parsed document with text and metadata

    Raises:
        ValueError: If file format is not supported
        FileNotFoundError: If file doesn't exist
    """
    if not isinstance(file_path, Path):
        file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    # Get file extension (lowercase, without dot)
    extension = file_path.suffix.lower().lstrip('.')

    # Route to appropriate parser
    parser_map = {
        'pdf': parse_pdf,
        'docx': parse_docx,
        'doc': parse_docx,
        'pptx': parse_pptx,
        'ppt': parse_pptx,
        'txt': parse_text,
        'md': parse_text,
        'csv': parse_spreadsheet,
        'xlsx': parse_spreadsheet,
        'xls': parse_spreadsheet,
    }

    parser = parser_map.get(extension)

    if parser is None:
        raise ValueError(
            f"Unsupported file format: .{extension}. "
            f"Supported formats: {', '.join(parser_map.keys())}"
        )

    logger.info(f"Routing {file_path.name} to {parser.__name__}")
    return parser(file_path)
