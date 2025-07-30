"""
Module de stockage et persistance des données
"""
import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, List
from config import config

DATA_DIR = config.DATA_DIR
REPORTS_DIR = config.REPORTS_DIR



logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def ensure_directories():
    """Crée les répertoires nécessaires"""
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(REPORTS_DIR, exist_ok=True)

def save_search_results(results: List[Dict], query: str) -> bool:
    """
    Sauvegarde les résultats de recherche
    
    Args:
        results (List[Dict]): Résultats de recherche
        query (str): Requête utilisée
        
    Returns:
        bool: Succès de la sauvegarde
    """
    try:
        ensure_directories()
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"search_{timestamp}.json"
        filepath = os.path.join(DATA_DIR, filename)
        
        data = {
            'query': query,
            'timestamp': timestamp,
            'results_count': len(results),
            'results': results
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Résultats sauvegardés : {filepath}")
        return True
        
    except Exception as e:
        logger.error(f"Erreur sauvegarde recherche : {e}")
        return False

def save_analysis_results(analysis_data: List[Dict]) -> bool:
    """
    Sauvegarde les résultats d'analyse
    
    Args:
        analysis_data (List[Dict]): Données d'analyse
        
    Returns:
        bool: Succès de la sauvegarde
    """
    try:
        ensure_directories()
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"analysis_{timestamp}.json"
        filepath = os.path.join(DATA_DIR, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(analysis_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Analyse sauvegardée : {filepath}")
        return True
        
    except Exception as e:
        logger.error(f"Erreur sauvegarde analyse : {e}")
        return False

def save_report(data: Any, filename: str, is_text: bool = False) -> bool:
    """
    Sauvegarde un rapport
    
    Args:
        data (Any): Données à sauvegarder
        filename (str): Nom du fichier
        is_text (bool): True si texte, False si JSON
        
    Returns:
        bool: Succès de la sauvegarde
    """
    try:
        ensure_directories()
        filepath = os.path.join(REPORTS_DIR, filename)
        
        if is_text:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(str(data))
        else:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Rapport sauvegardé : {filepath}")
        return True
        
    except Exception as e:
        logger.error(f"Erreur sauvegarde rapport : {e}")
        return False

def load_latest_report() -> Dict:
    """
    Charge le dernier rapport généré
    
    Returns:
        Dict: Données du rapport ou dict vide
    """
    try:
        ensure_directories()
        
        # Lister les fichiers de rapport JSON
        report_files = [
            f for f in os.listdir(REPORTS_DIR) 
            if f.endswith('.json') and f.startswith('nlp_watch_')
        ]
        
        if not report_files:
            return {}
        
        # Trier par date de modification
        report_files.sort(key=lambda x: os.path.getmtime(
            os.path.join(REPORTS_DIR, x)
        ), reverse=True)
        
        latest_file = report_files[0]
        filepath = os.path.join(REPORTS_DIR, latest_file)
        
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
            
    except Exception as e:
        logger.error(f"Erreur chargement rapport : {e}")
        return {}
