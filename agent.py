"""
Agent principal de veille technologique NLP - Version corrigée
"""
import time
import logging
import traceback
from typing import List, Dict, Optional
from datetime import datetime

# Configuration du logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('nlp_agent.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Import de la configuration
from config import config, NLP_KEYWORDS, MAX_SEARCH_RESULTS

# Import des modules (noms corrigés)
from modules.search import search_nlp_papers, search_web
from modules.extraction import extract_content
from modules.analysis import analyze_nlp_relevance, extract_key_insights
from modules.synthesis import generate_tech_watch_report, save_reports
from modules.storage import save_search_results, save_analysis_results
from modules.security import validate_url


class TechWatchAgent:
    """Agent principal de veille technologique"""
    
    def __init__(self):
        self.config = config
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        logger.info(f"🤖 Agent initialisé - Session: {self.session_id}")
    
    def run_full_cycle(self, custom_keywords: List[str] = None) -> Dict:
        """
        Lance un cycle complet de veille technologique
        
        Args:
            custom_keywords: Mots-clés personnalisés (optionnel)
            
        Returns:
            Dict: Rapport de veille généré
        """
        logger.info(f"🚀 Démarrage du cycle de veille - Session: {self.session_id}")
        
        cycle_data = {
            'session_id': self.session_id,
            'start_time': datetime.now(),
            'keywords_used': custom_keywords or NLP_KEYWORDS,
            'phases_completed': [],
            'errors': []
        }
        
        try:
            # Phase 1: Recherche
            search_results = self._search_phase(cycle_data)
            if not search_results:
                return self._create_error_report(cycle_data, "Aucun résultat de recherche")
            
            # Phase 2: Extraction
            extracted_content = self._extraction_phase(search_results, cycle_data)
            if not extracted_content:
                return self._create_error_report(cycle_data, "Aucun contenu extrait")
            
            # Phase 3: Analyse
            analyzed_content = self._analysis_phase(extracted_content, cycle_data)
            if not analyzed_content:
                return self._create_error_report(cycle_data, "Aucune analyse réalisée")
            
            # Phase 4: Synthèse et rapport
            report = self._synthesis_phase(analyzed_content, cycle_data)
            
            cycle_data['end_time'] = datetime.now()
            cycle_data['duration'] = (cycle_data['end_time'] - cycle_data['start_time']).total_seconds()
            
            logger.info(f"✅ Cycle terminé avec succès en {cycle_data['duration']:.1f}s")
            return report
            
        except Exception as e:
            logger.error(f"❌ Erreur critique dans le cycle: {e}")
            logger.error(traceback.format_exc())
            return self._create_error_report(cycle_data, str(e))
    
    def _search_phase(self, cycle_data: Dict) -> List[Dict]:
        """Phase 1: Recherche web"""
        logger.info("📡 Phase 1: Recherche web")
        
        try:
            keywords = cycle_data['keywords_used']
            search_results = search_nlp_papers(keywords)
            
            if search_results:
                logger.info(f"Trouvé {len(search_results)} résultats de recherche")
                save_search_results(search_results, ", ".join(keywords))
                cycle_data['phases_completed'].append('search')
            else:
                logger.warning("Aucun résultat de recherche trouvé")
            
            return search_results
            
        except Exception as e:
            error_msg = f"Erreur phase recherche: {e}"
            logger.error(error_msg)
            cycle_data['errors'].append(error_msg)
            return []
    
    def _extraction_phase(self, search_results: List[Dict], cycle_data: Dict) -> List[Dict]:
        """Phase 2: Extraction de contenu"""
        logger.info("📄 Phase 2: Extraction de contenu")
        
        extracted_content = []
        successful_extractions = 0
        failed_extractions = 0
        
        try:
            for i, result in enumerate(search_results[:MAX_SEARCH_RESULTS]):
                try:
                    url = result.get('url')
                    logger.debug(f"Extraction {i+1}/{min(len(search_results), MAX_SEARCH_RESULTS)}: {url}")
                    
                    if not validate_url(url):
                        logger.warning(f"URL invalide ignorée: {url}")
                        failed_extractions += 1
                        continue
                    
                    content = extract_content(url)
                    if content:
                        # Enrichissement avec métadonnées de recherche
                        content.update({
                            'search_title': result.get('title'),
                            'search_snippet': result.get('snippet'),
                            'search_timestamp': result.get('timestamp'),
                            'extraction_order': i + 1
                        })
                        extracted_content.append(content)
                        successful_extractions += 1
                    else:
                        failed_extractions += 1
                    
                    # Pause pour éviter la surcharge
                    time.sleep(1)
                    
                except Exception as e:
                    logger.warning(f"Échec extraction {url}: {e}")
                    failed_extractions += 1
                    continue
            
            logger.info(f"Extraction terminée: {successful_extractions} succès, {failed_extractions} échecs")
            
            if extracted_content:
                cycle_data['phases_completed'].append('extraction')
            
            return extracted_content
            
        except Exception as e:
            error_msg = f"Erreur phase extraction: {e}"
            logger.error(error_msg)
            cycle_data['errors'].append(error_msg)
            return []
    
    def _analysis_phase(self, extracted_content: List[Dict], cycle_data: Dict) -> List[Dict]:
        """Phase 3: Analyse NLP"""
        logger.info("🧠 Phase 3: Analyse NLP")
        
        analyzed_content = []
        analysis_stats = {'total': 0, 'success': 0, 'failed': 0}
        
        try:
            for i, content in enumerate(extracted_content):
                try:
                    logger.debug(f"Analyse {i+1}/{len(extracted_content)}: {content.get('title', 'Sans titre')}")
                    
                    analysis = analyze_nlp_relevance(
                        content.get('content', ''),
                        content.get('title', '')
                    )
                    
                    analyzed_item = {
                        **content,
                        'analysis': analysis,
                        'analysis_timestamp': datetime.now().isoformat()
                    }
                    
                    analyzed_content.append(analyzed_item)
                    analysis_stats['success'] += 1
                    
                    logger.debug(f"Score de pertinence: {analysis.get('relevance_score', 0)}")
                    
                    # Pause pour respecter les limites API
                    time.sleep(2)
                    
                except Exception as e:
                    logger.warning(f"Échec analyse document {i+1}: {e}")
                    analysis_stats['failed'] += 1
                    continue
                
                analysis_stats['total'] += 1
            
            logger.info(f"Analyse terminée: {analysis_stats['success']} succès, {analysis_stats['failed']} échecs")
            
            if analyzed_content:
                save_analysis_results(analyzed_content)
                cycle_data['phases_completed'].append('analysis')
                cycle_data['analysis_stats'] = analysis_stats
            
            return analyzed_content
            
        except Exception as e:
            error_msg = f"Erreur phase analyse: {e}"
            logger.error(error_msg)
            cycle_data['errors'].append(error_msg)
            return []
    
    def _synthesis_phase(self, analyzed_content: List[Dict], cycle_data: Dict) -> Dict:
        """Phase 4: Synthèse et génération de rapport"""
        logger.info("📊 Phase 4: Génération du rapport")
        
        try:
            # Génération du rapport principal
            report = generate_tech_watch_report(analyzed_content)
            
            # Ajout des métadonnées de session
            report['session_metadata'] = {
                'session_id': cycle_data['session_id'],
                'duration_seconds': (datetime.now() - cycle_data['start_time']).total_seconds(),
                'phases_completed': cycle_data['phases_completed'],
                'errors_count': len(cycle_data['errors'])
            }
            
            # Extraction des insights globaux
            try:
                logger.info("Extraction des insights globaux...")
                global_insights = extract_key_insights(analyzed_content)
                report['global_insights'] = global_insights
            except Exception as e:
                logger.warning(f"Échec extraction insights globaux: {e}")
                report['global_insights'] = {}
            
            # Sauvegarde des rapports
            try:
                save_success = save_reports(report)
                if save_success:
                    logger.info("✅ Rapports sauvegardés avec succès")
                    cycle_data['phases_completed'].append('synthesis')
                else:
                    logger.warning("⚠️ Problème lors de la sauvegarde des rapports")
            except Exception as e:
                logger.error(f"Erreur sauvegarde rapports: {e}")
            
            return report
            
        except Exception as e:
            error_msg = f"Erreur phase synthèse: {e}"
            logger.error(error_msg)
            cycle_data['errors'].append(error_msg)
            return self._create_error_report(cycle_data, error_msg)
    
    def _create_error_report(self, cycle_data: Dict, error_message: str) -> Dict:
        """Crée un rapport d'erreur"""
        return {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'report_id': f"error_{cycle_data['session_id']}",
                'status': 'error',
                'error_message': error_message
            },
            'session_metadata': cycle_data,
            'summary': {
                'total_documents_analyzed': 0,
                'relevant_documents': 0,
                'relevance_rate': 0.0,
                'average_relevance_score': 0.0
            }
        }
    
    def run_targeted_search(self, query: str, max_results: int = 10) -> Dict:
        """
        Recherche ciblée sur un sujet spécifique
        
        Args:
            query: Requête de recherche
            max_results: Nombre maximum de résultats
            
        Returns:
            Dict: Résultats de la recherche ciblée
        """
        logger.info(f"🎯 Recherche ciblée: {query}")
        
        try:
            # Recherche
            results = search_web(query, max_results)
            
            if not results:
                return {'error': 'Aucun résultat trouvé', 'query': query}
            
            # Analyse rapide des premiers résultats
            analyzed_results = []
            
            for result in results[:5]:  # Limiter à 5 pour l'analyse rapide
                try:
                    url = result.get('url')
                    logger.debug(f"Analyse rapide: {url}")
                    
                    content = extract_content(url)
                    if content:
                        analysis = analyze_nlp_relevance(
                            content.get('content', ''),
                            content.get('title', '')
                        )
                        
                        analyzed_results.append({
                            **content,
                            'analysis': analysis,
                            'search_metadata': result
                        })
                    
                    time.sleep(1)  # Pause entre extractions
                    
                except Exception as e:
                    logger.warning(f"Erreur analyse rapide {result.get('url')}: {e}")
                    continue
            
            return {
                'query': query,
                'total_found': len(results),
                'analyzed_count': len(analyzed_results),
                'results': analyzed_results,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erreur recherche ciblée: {e}")
            return {'error': str(e), 'query': query}


# Fonctions globales pour compatibilité
def run_tech_watch_cycle(custom_keywords: List[str] = None) -> Dict:
    """Lance un cycle complet de veille - Interface globale"""
    agent = TechWatchAgent()
    return agent.run_full_cycle(custom_keywords)

def run_targeted_search(query: str, max_results: int = 10) -> Dict:
    """Recherche ciblée - Interface globale"""
    agent = TechWatchAgent()
    return agent.run_targeted_search(query, max_results)

def monitor_keywords(keywords: List[str], check_interval: int = 3600) -> None:
    """
    Surveillance continue de mots-clés
    
    Args:
        keywords: Liste des mots-clés à surveiller
        check_interval: Intervalle en secondes entre les vérifications
    """
    import schedule
    
    agent = TechWatchAgent()
    
    def check_keywords():
        logger.info(f"🔍 Vérification programmée - {datetime.now()}")
        try:
            report = agent.run_full_cycle(keywords)
            
            # Compter les documents très pertinents
            relevant_count = 0
            if 'detailed_analysis' in report:
                relevant_count = len([
                    item for item in report['detailed_analysis']
                    if item.get('analysis', {}).get('relevance_score', 0) > 8
                ])
            
            if relevant_count > 0:
                logger.info(f"🚨 {relevant_count} documents très pertinents trouvés!")
            else:
                logger.info("ℹ️ Aucun document très pertinent trouvé")
                
        except Exception as e:
            logger.error(f"Erreur surveillance programmée: {e}")
    
    try:
        # Programmation de la surveillance
        schedule.every(check_interval).seconds.do(check_keywords)
        logger.info(f"📅 Surveillance programmée toutes les {check_interval/3600:.1f}h")
        
        # Boucle principale
        while True:
            schedule.run_pending()
            time.sleep(60)  # Vérifier chaque minute
            
    except KeyboardInterrupt:
        logger.info("🛑 Surveillance interrompue par l'utilisateur")
    except Exception as e:
        logger.error(f"Erreur boucle surveillance: {e}")


if __name__ == "__main__":
    try:
        # Test de l'agent
        agent = TechWatchAgent()
        report = agent.run_full_cycle()
        
        if 'error_message' not in report.get('metadata', {}):
            print(f"✅ Rapport généré: {report.get('metadata', {}).get('report_id', 'unknown')}")
        else:
            print(f"❌ Erreur: {report['metadata']['error_message']}")
            
    except Exception as e:
        logger.error(f"Erreur exécution principale: {e}")
        print(f"❌ Erreur critique: {e}")