"""
Module de recherche web utilisant DuckDuckGo
"""
import time
import logging
from typing import List, Dict, Optional
from duckduckgo_search import DDGS
from modules.security import sanitize_query, validate_url

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def search_web(query: str, max_results: int = 10) -> List[Dict]:
    """
    Recherche web avec DuckDuckGo
    
    Args:
        query (str): Requête de recherche
        max_results (int): Nombre maximum de résultats
        
    Returns:
        List[Dict]: Liste des résultats de recherche
    """
    try:
        # Sécurisation de la requête
        clean_query = sanitize_query(query)
        if not clean_query:
            logger.error("Requête invalide après nettoyage")
            return []
        
        logger.info(f"Recherche : {clean_query}")
        
        # Recherche avec DuckDuckGo
        with DDGS() as ddgs:
            results = []
            for result in ddgs.text(clean_query, max_results=max_results):
                if validate_url(result.get('href', '')):
                    results.append({
                        'title': result.get('title', ''),
                        'url': result.get('href', ''),
                        'snippet': result.get('body', ''),
                        'timestamp': time.time()
                    })
                
                if len(results) >= max_results:
                    break
                    
        logger.info(f"Trouvé {len(results)} résultats")
        return results
        
    except Exception as e:
        logger.error(f"Erreur lors de la recherche : {e}")
        return []

def search_nlp_papers(keywords: List[str]) -> List[Dict]:
    """
    Recherche spécialisée pour les papiers NLP
    
    Args:
        keywords (List[str]): Mots-clés NLP
        
    Returns:
        List[Dict]: Résultats de recherche combinés
    """
    all_results = []
    
    for keyword in keywords:
        # Recherche académique
        academic_query = f"site:arxiv.org {keyword}"
        academic_results = search_web(academic_query, max_results=5)
        
        # Recherche générale
        general_query = f"{keyword} 2024 research"
        general_results = search_web(general_query, max_results=5)
        
        all_results.extend(academic_results)
        all_results.extend(general_results)
        
        # Pause pour éviter le rate limiting
        time.sleep(1)
    
    # Déduplication par URL
    unique_results = {}
    for result in all_results:
        url = result.get('url')
        if url and url not in unique_results:
            unique_results[url] = result
            
    return list(unique_results.values())
