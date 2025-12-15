import logging
import io
from typing import Optional

logger = logging.getLogger("core.pdf_loader")

try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None

def extract_text_from_pdf(file_bytes: bytes) -> str:
    """
    Extract text from a PDF file (in-memory bytes).
    
    Args:
        file_bytes (bytes): The raw bytes of the PDF.
        
    Returns:
        str: The extracted text.
    """
    if PdfReader is None:
        return "Error: pypdf library not installed. Please install it with `pip install pypdf`."

    try:
        pdf_file = io.BytesIO(file_bytes)
        reader = PdfReader(pdf_file)
        
        text = []
        for i, page in enumerate(reader.pages):
            page_text = page.extract_text()
            if page_text:
                text.append(page_text)
        
        full_text = "\n\n".join(text)
        logger.info(f"Extracted {len(full_text)} chars from PDF.")
        return full_text
        
    except Exception as e:
        logger.error(f"Failed to read PDF: {e}")
        return f"Error reading PDF: {str(e)}"
