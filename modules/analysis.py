"""
Module d'analyse NLP avec OpenAI - Version améliorée
"""
import openai
import json
import logging
from typing import Dict, List, Optional, Union
from config import config

# Configuration
OPENAI_API_KEY = config.OPENAI_API_KEY
MAX_CONTENT_LENGTH = 4000
MAX_RETRIES = 3

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration OpenAI
openai.api_key = OPENAI_API_KEY

def safe_json_parse(text: str) -> Dict:
    """
    Parse JSON de manière sécurisée avec fallback
    
    Args:
        text (str): Texte à parser
        
    Returns:
        Dict: Résultat parsé ou structure par défaut
    """
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Extraction simple par regex en cas d'échec
        import re
        
        # Extraction du score de pertinence
        relevance_match = re.search(r'relevance_score["\s]*:[\s]*(\d+)', text)
        relevance_score = int(relevance_match.group(1)) if relevance_match else 5
        
        # Extraction des domaines NLP
        domains_match = re.search(r'nlp_domains["\s]*:[\s]*\[(.*?)\]', text, re.DOTALL)
        nlp_domains = []
        if domains_match:
            domains_text = domains_match.group(1)
            nlp_domains = [d.strip(' "\'') for d in domains_text.split(',') if d.strip()]
        
        return {
            "relevance_score": relevance_score,
            "nlp_domains": nlp_domains,
            "techniques": [],
            "novelty_score": 5,
            "summary": text[:300],
            "keywords": []
        }

def create_nlp_analysis_prompt(content: str, title: str = "") -> str:
    """
    Crée un prompt optimisé pour l'analyse NLP
    
    Args:
        content (str): Contenu à analyser
        title (str): Titre du document
        
    Returns:
        str: Prompt structuré
    """
    # Troncature intelligente du contenu
    truncated_content = content[:MAX_CONTENT_LENGTH]
    if len(content) > MAX_CONTENT_LENGTH:
        truncated_content += "... [contenu tronqué]"
    
    return f"""
Analysez ce contenu scientifique pour évaluer sa pertinence en Traitement Automatique des Langues (TAL/NLP).

**Titre :** {title}

**Contenu :**
{truncated_content}

**Instructions d'analyse :**
1. Évaluez la pertinence NLP sur une échelle de 0 à 10
2. Identifiez les domaines NLP spécifiques abordés
3. Listez les techniques/modèles/architectures mentionnés
4. Évaluez la nouveauté/innovation (0-10)
5. Rédigez un résumé en français (maximum 3 phrases)
6. Extrayez les mots-clés techniques pertinents

**Domaines NLP à considérer :**
- Compréhension du langage naturel
- Génération de texte
- Traduction automatique
- Analyse de sentiment
- Extraction d'information
- Question-réponse
- Résumé automatique
- Reconnaissance d'entités nommées
- Classification de texte
- Modèles de langage (LLM)

**Format de réponse OBLIGATOIRE (JSON strict) :**
{{
    "relevance_score": <nombre_entre_0_et_10>,
    "nlp_domains": ["domaine1", "domaine2"],
    "techniques": ["technique1", "technique2"],
    "novelty_score": <nombre_entre_0_et_10>,
    "summary": "Résumé en français en 3 phrases maximum",
    "keywords": ["mot-clé1", "mot-clé2"]
}}
"""

def analyze_nlp_relevance(content: str, title: str = "") -> Dict:
    """
    Analyse la pertinence NLP d'un contenu avec retry et validation
    
    Args:
        content (str): Contenu à analyser
        title (str): Titre du document
        
    Returns:
        Dict: Résultats de l'analyse
    """
    if not content.strip():
        return {
            "relevance_score": 0,
            "nlp_domains": [],
            "techniques": [],
            "novelty_score": 0,
            "summary": "Contenu vide",
            "keywords": [],
            "error": "Contenu vide"
        }
    
    for attempt in range(MAX_RETRIES):
        try:
            prompt = create_nlp_analysis_prompt(content, title)
            
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,  # Plus déterministe
                max_tokens=1000
            )
            
            result = response.choices[0].message.content
            analysis = safe_json_parse(result)
            
            # Validation des résultats
            analysis = validate_analysis_result(analysis)
            
            logger.info(f"Analyse réussie (tentative {attempt + 1}): score={analysis.get('relevance_score', 0)}")
            return analysis
            
        except Exception as e:
            logger.warning(f"Tentative {attempt + 1} échouée: {e}")
            if attempt == MAX_RETRIES - 1:
                logger.error(f"Toutes les tentatives ont échoué pour l'analyse: {e}")
                return {
                    "relevance_score": 0,
                    "nlp_domains": [],
                    "techniques": [],
                    "novelty_score": 0,
                    "summary": "Erreur d'analyse après plusieurs tentatives",
                    "keywords": [],
                    "error": str(e)
                }

def validate_analysis_result(analysis: Dict) -> Dict:
    """
    Valide et normalise les résultats d'analyse
    
    Args:
        analysis (Dict): Résultats bruts
        
    Returns:
        Dict: Résultats validés
    """
    # Validation du score de pertinence
    relevance_score = analysis.get('relevance_score', 0)
    if not isinstance(relevance_score, (int, float)) or relevance_score < 0 or relevance_score > 10:
        analysis['relevance_score'] = 5
    
    # Validation des domaines NLP
    nlp_domains = analysis.get('nlp_domains', [])
    if not isinstance(nlp_domains, list):
        analysis['nlp_domains'] = []
    
    # Validation des techniques
    techniques = analysis.get('techniques', [])
    if not isinstance(techniques, list):
        analysis['techniques'] = []
    
    # Validation du score de nouveauté
    novelty_score = analysis.get('novelty_score', 0)
    if not isinstance(novelty_score, (int, float)) or novelty_score < 0 or novelty_score > 10:
        analysis['novelty_score'] = 5
    
    # Validation du résumé
    summary = analysis.get('summary', '')
    if not isinstance(summary, str) or len(summary) > 1000:
        analysis['summary'] = str(summary)[:1000] if summary else "Résumé non disponible"
    
    # Validation des mots-clés
    keywords = analysis.get('keywords', [])
    if not isinstance(keywords, list):
        analysis['keywords'] = []
    
    return analysis

def extract_key_insights(analyzed_contents: List[Dict]) -> Dict:
    """
    Extrait les insights clés d'une liste de contenus analysés
    
    Args:
        analyzed_contents (List[Dict]): Contenus déjà analysés
        
    Returns:
        Dict: Insights extraits
    """
    try:
        # Filtrer le contenu pertinent
        relevant_contents = [
            content for content in analyzed_contents 
            if content.get('analysis', {}).get('relevance_score', 0) > 6
        ]
        
        if not relevant_contents:
            return {
                "trends": [],
                "technologies": [],
                "challenges": [],
                "opportunities": [],
                "key_players": []
            }
        
        # Préparer le contexte d'analyse
        insights_context = []
        for content in relevant_contents[:5]:  # Limiter à 5 documents
            analysis = content.get('analysis', {})
            context = f"""
Titre: {content.get('title', 'Sans titre')}
Domaines NLP: {', '.join(analysis.get('nlp_domains', []))}
Techniques: {', '.join(analysis.get('techniques', []))}
Résumé: {analysis.get('summary', '')}
"""
            insights_context.append(context)
        
        combined_context = "\n---\n".join(insights_context)
        
        prompt = f"""
Analysez ces documents de recherche en TAL/NLP et identifiez les tendances principales :

{combined_context}

Basé sur ces analyses, identifiez :

1. **Tendances émergentes** : Quelles sont les nouvelles directions de recherche ?
2. **Technologies populaires** : Quels modèles, techniques ou outils sont les plus mentionnés ?
3. **Défis actuels** : Quels problèmes la communauté TAL tente-t-elle de résoudre ?
4. **Opportunités de recherche** : Quelles sont les pistes prometteuses ?
5. **Acteurs clés** : Auteurs, institutions ou entreprises influents mentionnés

Répondez en format JSON strict :
{{
    "trends": ["tendance1", "tendance2"],
    "technologies": ["tech1", "tech2"],
    "challenges": ["défi1", "défi2"],
    "opportunities": ["opportunité1", "opportunité2"],
    "key_players": ["acteur1", "acteur2"]
}}
"""
        
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=1200
        )
        
        result = response.choices[0].message.content
        insights = safe_json_parse(result)
        
        # Validation des insights
        default_insights = {
            "trends": [],
            "technologies": [],
            "challenges": [],
            "opportunities": [],
            "key_players": []
        }
        
        for key in default_insights:
            if key not in insights or not isinstance(insights[key], list):
                insights[key] = default_insights[key]
        
        logger.info("Extraction d'insights réussie")
        return insights
        
    except Exception as e:
        logger.error(f"Erreur extraction insights : {e}")
        return {
            "trends": [],
            "technologies": [],
            "challenges": [],
            "opportunities": [],
            "key_players": [],
            "error": str(e)
        }