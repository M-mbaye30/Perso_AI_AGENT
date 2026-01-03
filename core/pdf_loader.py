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
    Extrait le texte d'un fichier PDF (octets en mémoire).
    
    Args:
        file_bytes (bytes) : Les octets bruts du PDF.
        
    Returns:
        str : Le texte extrait.
    """
    if PdfReader is None:
        return "Erreur : la bibliothèque pypdf n'est pas installée. Veuillez l'installer avec `pip install pypdf`."

    try:
        pdf_file = io.BytesIO(file_bytes)
        reader = PdfReader(pdf_file)
        
        text = []
        for i, page in enumerate(reader.pages):
            page_text = page.extract_text()
            if page_text:
                text.append(page_text)
        
        full_text = "\n\n".join(text)
        logger.info(f"Extraction de {len(full_text)} caractères du PDF.")
        return full_text
        
    except Exception as e:
        logger.error(f"Échec de la lecture du PDF : {e}")
        return f"Erreur lors de la lecture du PDF : {str(e)}"
