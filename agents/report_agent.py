from typing import Dict, Any
import logging
from core.agent_base import BaseAgent
from core.llm_client import OllamaClient

logger = logging.getLogger("agents.report")

class ReportAgent(BaseAgent):
    """
    Agent spécialisé dans la génération de rapports d'étude structurés.
    Produit des rapports professionnels avec sections standardisées.
    """
    
    def __init__(self, llm_client: OllamaClient):
        super().__init__(
            name="ReportAgent",
            description="Génère des rapports d'étude structurés et professionnels sur un document ou un sujet."
        )
        self.llm_client = llm_client

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Génère un rapport d'étude structuré.
        
        Input Keys:
            - text (str): Le contenu du document ou le sujet à analyser.
            - instruction (str): Instructions spécifiques pour le rapport.
            
        Returns:
            - report (str): Le rapport complet en Markdown.
            - title (str): Le titre du rapport.
        """
        self.validate_input(input_data, ["text"])
        
        content = input_data["text"]
        instruction = input_data.get("instruction", "Génère un rapport d'étude complet")
        
        logger.info(f"Génération d'un rapport structuré : {instruction[:50]}...")
        
        system_prompt = """Tu es un expert en rédaction de rapports professionnels.
Tu dois générer un rapport d'étude structuré et complet en français.

STRUCTURE OBLIGATOIRE DU RAPPORT:
1. **Titre** - Un titre clair et professionnel
2. **Résumé Exécutif** - Synthèse en 3-5 lignes
3. **Introduction** - Contexte et objectifs de l'étude
4. **Analyse Détaillée** - Points principaux avec sous-sections
5. **Constats Clés** - Liste des observations importantes
6. **Recommandations** - Actions suggérées, numérotées
7. **Conclusion** - Synthèse finale

RÈGLES:
- Utilise le format Markdown
- Sois professionnel et objectif
- Inclus des bullet points pour la lisibilité
- Cite des éléments spécifiques du document si disponible
"""
        
        prompt = f"""Instruction: {instruction}

Contenu à analyser:
{content[:15000]}

Génère maintenant le rapport d'étude complet en suivant la structure demandée."""
        
        try:
            response = self.llm_client.generate(prompt, system_prompt=system_prompt)
            
            # Extraire le titre de la réponse
            lines = response.strip().split('\n')
            title = "Rapport d'Étude"
            for line in lines:
                if line.startswith('# '):
                    title = line.replace('# ', '').strip()
                    break
            
            return {
                "report": response,
                "title": title,
                "format": "markdown"
            }
            
        except Exception as e:
            logger.error(f"La génération du rapport a échoué : {e}")
            return {"erreur": str(e)}
