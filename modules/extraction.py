"""
Module d'extraction de contenu web
"""

import requests
import logging
import time
from typing import Dict, Optional
from bs4 import BeautifulSoup
from modules.security import sanitize_content, validate_content_length

# Configuration
MAX_CONTENT_LENGTH = 50000  # Longueur maximale du contenu

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_content(url: str) -> Optional[Dict]:
    """
    Extrait le contenu d'une page web
    
    Args:
        url (str): URL de la page
        
    Returns:
        Optional[Dict]: Contenu extrait ou None
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (compatible; NLP-Research-Bot/1.0)'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Suppression des scripts et styles
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
        
        # Extraction du titre
        title = soup.find('title')
        title_text = title.get_text().strip() if title else ""
        
        # Extraction du contenu principal
        content_selectors = [
            'article', 'main', '.content', '.post', '.paper-content',
            '.abstract', '.entry-content', '#content', '.post-content',
            '.article-content', '.blog-content'
        ]
        
        content_text = ""
        for selector in content_selectors:
            elements = soup.select(selector)
            if elements:
                content_text = elements[0].get_text()
                break
        
        # Si pas de sélecteur spécifique, prendre tout le body
        if not content_text:
            body = soup.find('body')
            content_text = body.get_text() if body else ""
        
        # Nettoyage du contenu
        clean_content = sanitize_content(content_text)
        
        # Validation de la longueur
        if len(clean_content) > MAX_CONTENT_LENGTH:
            logger.warning(f"Contenu trop long pour {url}, troncature à {MAX_CONTENT_LENGTH} caractères")
            clean_content = clean_content[:MAX_CONTENT_LENGTH]
        
        if len(clean_content.strip()) < 100:
            logger.warning(f"Contenu trop court pour {url}")
            return None
        
        return {
            'url': url,
            'title': sanitize_content(title_text),
            'content': clean_content,
            'word_count': len(clean_content.split()),
            'extraction_time': time.time()
        }
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Erreur réseau pour {url}: {e}")
        return None
    except Exception as e:
        logger.error(f"Erreur extraction {url}: {e}")
        return None

def extract_arxiv_abstract(url: str) -> Optional[str]:
    """
    Extraction spécialisée pour les abstracts arXiv
    
    Args:
        url (str): URL arXiv
        
    Returns:
        Optional[str]: Abstract extrait
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (compatible; NLP-Research-Bot/1.0)'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Sélecteur spécifique pour arXiv
        abstract_block = soup.find('blockquote', class_='abstract')
        if abstract_block:
            abstract_text = abstract_block.get_text()
            # Nettoyer le préfixe "Abstract:"
            return abstract_text.replace('Abstract:', '').strip()
        
        # Alternative pour les nouvelles pages arXiv
        abstract_div = soup.find('div', class_='abstract')
        if abstract_div:
            abstract_text = abstract_div.get_text()
            return abstract_text.replace('Abstract:', '').strip()
            
        return None
        
    except Exception as e:
        logger.error(f"Erreur extraction arXiv {url}: {e}")
        return None

def extract_academic_content(url: str) -> Optional[Dict]:
    """
    Extraction spécialisée pour le contenu académique
    
    Args:
        url (str): URL de la page académique
        
    Returns:
        Optional[Dict]: Contenu académique extrait
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (compatible; Academic-Research-Bot/1.0)'
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Suppression des éléments non pertinents
        for element in soup(["script", "style", "nav", "footer", "header", "aside"]):
            element.decompose()
        
        # Extraction du titre
        title = ""
        title_selectors = ['h1', 'title', '.paper-title', '.article-title']
        for selector in title_selectors:
            title_elem = soup.select_one(selector)
            if title_elem:
                title = title_elem.get_text().strip()
                break
        
        # Extraction de l'abstract
        abstract = ""
        abstract_selectors = ['.abstract', '#abstract', '.paper-abstract']
        for selector in abstract_selectors:
            abstract_elem = soup.select_one(selector)
            if abstract_elem:
                abstract = abstract_elem.get_text().strip()
                break
        
        # Extraction du contenu principal
        content = extract_content(url)
        if content:
            return {
                **content,
                'abstract': sanitize_content(abstract),
                'type': 'academic'
            }
        
        return None
        
    except Exception as e:
        logger.error(f"Erreur extraction contenu académique {url}: {e}")
        return None