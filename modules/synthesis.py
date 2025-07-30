"""
Module de synthèse et génération de rapports
"""
import json
import time
from datetime import datetime
from typing import List, Dict
from modules.storage import save_report

def generate_tech_watch_report(analyzed_content: List[Dict]) -> Dict:
    """
    Génère un rapport de veille technologique
    
    Args:
        analyzed_content (List[Dict]): Contenus analysés
        
    Returns:
        Dict: Rapport structuré
    """
    # Filtrer le contenu pertinent (score > 6)
    relevant_content = [
        item for item in analyzed_content 
        if item.get('analysis', {}).get('relevance_score', 0) > 6
    ]
    
    # Statistiques
    total_documents = len(analyzed_content)
    relevant_documents = len(relevant_content)
    avg_relevance = sum(
        item.get('analysis', {}).get('relevance_score', 0) 
        for item in analyzed_content
    ) / max(total_documents, 1)
    
    # Extraction des domaines NLP
    all_domains = []
    all_techniques = []
    for item in relevant_content:
        analysis = item.get('analysis', {})
        all_domains.extend(analysis.get('nlp_domains', []))
        all_techniques.extend(analysis.get('techniques', []))
    
    # Comptage des domaines
    domain_counts = {}
    for domain in all_domains:
        domain_counts[domain] = domain_counts.get(domain, 0) + 1
    
    # Top domaines
    top_domains = sorted(domain_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    
    # Génération du rapport
    report = {
        'metadata': {
            'generated_at': datetime.now().isoformat(),
            'report_id': f"nlp_watch_{int(time.time())}",
            'version': '1.0'
        },
        'summary': {
            'total_documents_analyzed': total_documents,
            'relevant_documents': relevant_documents,
            'relevance_rate': relevant_documents / max(total_documents, 1),
            'average_relevance_score': round(avg_relevance, 2)
        },
        'insights': {
            'top_nlp_domains': top_domains,
            'emerging_techniques': list(set(all_techniques))[:10],
            'high_impact_papers': [
                {
                    'title': item.get('title', ''),
                    'url': item.get('url', ''),
                    'relevance_score': item.get('analysis', {}).get('relevance_score', 0),
                    'summary': item.get('analysis', {}).get('summary', '')
                }
                for item in sorted(
                    relevant_content, 
                    key=lambda x: x.get('analysis', {}).get('relevance_score', 0), 
                    reverse=True
                )[:5]
            ]
        },
        'detailed_analysis': relevant_content
    }
    
    return report

def generate_markdown_report(report_data: Dict) -> str:
    """
    Génère un rapport au format Markdown
    
    Args:
        report_data (Dict): Données du rapport
        
    Returns:
        str: Rapport formaté en Markdown
    """
    metadata = report_data.get('metadata', {})
    summary = report_data.get('summary', {})
    insights = report_data.get('insights', {})
    
    markdown = f"""# 🤖 Rapport de Veille Technologique NLP

**Généré le :** {metadata.get('generated_at', 'N/A')}  
**ID du rapport :** {metadata.get('report_id', 'N/A')}

## 📊 Résumé Exécutif

- **Documents analysés :** {summary.get('total_documents_analyzed', 0)}
- **Documents pertinents :** {summary.get('relevant_documents', 0)}
- **Taux de pertinence :** {summary.get('relevance_rate', 0):.1%}
- **Score moyen de pertinence :** {summary.get('average_relevance_score', 0)}/10

## 🔥 Domaines NLP Tendances

"""
    
    for domain, count in insights.get('top_nlp_domains', []):
        markdown += f"- **{domain}** : {count} mentions\n"
    
    markdown += "\n## 🚀 Techniques Émergentes\n\n"
    
    for technique in insights.get('emerging_techniques', []):
        markdown += f"- {technique}\n"
    
    markdown += "\n## 📑 Papers à Impact Élevé\n\n"
    
    for paper in insights.get('high_impact_papers', []):
        markdown += f"""### {paper.get('title', 'Sans titre')}
**Score :** {paper.get('relevance_score', 0)}/10  
**Lien :** {paper.get('url', 'N/A')}  
**Résumé :** {paper.get('summary', 'Pas de résumé disponible')}

---

"""
    
    return markdown

def save_reports(report_data: Dict) -> bool:
    """
    Sauvegarde les rapports en JSON et Markdown
    
    Args:
        report_data (Dict): Données du rapport
        
    Returns:
        bool: Succès de la sauvegarde
    """
    try:
        report_id = report_data.get('metadata', {}).get('report_id', 'unknown')
        
        # Sauvegarde JSON
        json_success = save_report(report_data, f"{report_id}.json")
        
        # Sauvegarde Markdown
        markdown_content = generate_markdown_report(report_data)
        markdown_success = save_report(markdown_content, f"{report_id}.md", is_text=True)
        
        return json_success and markdown_success
        
    except Exception as e:
        print(f"Erreur sauvegarde rapports : {e}")
        return False


