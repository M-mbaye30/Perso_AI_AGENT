"""
Module de sécurité et validation
"""
import re
import validators
import bleach
import logging
from typing import Optional
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

# Configuration de sécurité
MAX_CONTENT_LENGTH = 50000
MIN_CONTENT_LENGTH = 100
MAX_SEARCH_RESULTS = 10

# Domaines autorisés pour l'extraction
ALLOWED_DOMAINS = [
    'arxiv.org',
    'scholar.google.com',
    'researchgate.net',
    'ieee.org',
    'acm.org',
    'springer.com',
    'sciencedirect.com',
    'nature.com',
    'openai.com',
    'huggingface.co',
    'github.com',
    'medium.com',
    'towardsdatascience.com',
    'ai.googleblog.com',
    'blog.openai.com',
    'research.google',
    'deepmind.com',
    'anthropic.com',
    'fr.shaip.com',
    'strategies-ia.net',
    'free-work.com',
    'manageengine.com',
    'bpifrance.fr'
]

# Mots-clés NLP (si pas disponibles depuis config)
NLP_KEYWORDS = [
    'natural language processing',
    'nlp',
    'transformer',
    'bert',
    'gpt',
    'language model',
    'deep learning',
    'machine learning',
    'ai',
    'artificial intelligence'
]

def sanitize_query(query: str) -> Optional[str]:
    """
    Nettoie et valide une requête de recherche
    
    Args:
        query (str): Requête brute
        
    Returns:
        Optional[str]: Requête nettoyée ou None
    """
    if not query or not isinstance(query, str):
        return None
    
    # Suppression des caractères dangereux
    query = re.sub(r'[<>"\']', '', query)
    
    # Limitation de longueur
    query = query[:200]
    
    # Suppression des espaces multiples
    query = re.sub(r'\s+', ' ', query).strip()
    
    if len(query) < 2:
        return None
    
    return query

def validate_content_length(content: str) -> bool:
    """
    Valide la longueur du contenu
    
    Args:
        content (str): Contenu à valider
        
    Returns:
        bool: True si la longueur est acceptable
    """
    if not content:
        return False
    
    content_length = len(content)
    
    if content_length < MIN_CONTENT_LENGTH:
        logger.warning(f"Contenu trop court: {content_length} caractères")
        return False
    
    if content_length > MAX_CONTENT_LENGTH:
        logger.warning(f"Contenu trop long: {content_length} caractères")
        return False
    
    return True

def validate_url(url: str) -> bool:
    """
    Valide une URL
    
    Args:
        url (str): URL à valider
        
    Returns:
        bool: True si valide
    """
    if not url or not isinstance(url, str):
        return False
    
    # Validation du format
    try:
        if not validators.url(url):
            return False
    except:
        return False
    
    # Vérification du protocole
    if not url.startswith(('http://', 'https://')):
        return False
    
    return True

def sanitize_content(content: str) -> str:
    """
    Nettoie le contenu extrait
    
    Args:
        content (str): Contenu brut
        
    Returns:
        str: Contenu nettoyé
    """
    if not content:
        return ""
    
    try:
        # Suppression des balises HTML
        content = bleach.clean(content, tags=[], strip=True)
        
        # Suppression des caractères de contrôle
        content = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', content)
        
        # Suppression des espaces multiples et normalisation
        content = re.sub(r'\s+', ' ', content)
        content = content.strip()
        
        return content
        
    except Exception as e:
        logger.error(f"Erreur lors du nettoyage du contenu: {e}")
        return str(content) if content else ""

def filter_sensitive_content(content: str) -> str:
    """
    Filtre le contenu sensible
    
    Args:
        content (str): Contenu à filtrer
        
    Returns:
        str: Contenu filtré
    """
    if not content:
        return ""
    
    # Liste des mots-clés sensibles à filtrer
    sensitive_patterns = [
        r'\b(?:password|passwd|pwd)\s*[:=]\s*\S+',
        r'\b(?:api[_-]?key|apikey)\s*[:=]\s*\S+',
        r'\b(?:token|auth)\s*[:=]\s*\S+',
    ]
    
    filtered_content = content
    for pattern in sensitive_patterns:
        filtered_content = re.sub(pattern, '[FILTERED]', filtered_content, flags=re.IGNORECASE)
    
    return filtered_content

def is_domain_allowed(url: str) -> bool:
    """
    Vérifie si le domaine est autorisé
    
    Args:
        url (str): URL à vérifier
        
    Returns:
        bool: True si domaine autorisé
    """
    try:
        domain = urlparse(url).netloc.lower()
        for allowed in ALLOWED_DOMAINS:
            if allowed in domain:
                return True
        return False
    except Exception as e:
        logger.error(f"Erreur lors de la validation du domaine: {e}")
        return False