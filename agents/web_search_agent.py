import logging
import json
from typing import Dict, Any, List
from duckduckgo_search import DDGS
from core.agent_base import BaseAgent
from core.llm_client import OllamaClient

logger = logging.getLogger("agents.web_search")

class WebSearchAgent(BaseAgent):
    """
    Agent avancé pour la recherche web avec décomposition, recherche multi-sources,
    et vérification croisée des résultats.
    """
    
    def __init__(self, llm_client: OllamaClient):
        super().__init__(
            name="WebSearchAgent",
            description="Exécute des recherches web approfondies, vérifie les sources et synthétise les informations issues de multiples recherches."
        )
        self.llm_client = llm_client

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Mener une recherche web complexe.
        """
        self.validate_input(input_data, ["instruction"])
        main_query = input_data["instruction"]
        
        logger.info(f"Démarrage de la recherche pour : {main_query}")

        # 1. Décomposition
        search_queries = self._decompose(main_query)
        if not search_queries:
            return {"erreur": "Échec de la décomposition de la requête en termes de recherche."}

        # 2. Recherche multi-sources (Action)
        all_results = []
        for q in search_queries:
            logger.info(f"Recherche de : {q}")
            results = self._search(q)
            if results:
                all_results.extend(results)
        
        # 3. Observation & Gestion des échecs
        if not all_results:
            return {
                "erreur": "Aucun résultat trouvé sur le web.",
                "details": f"Recherche effectuée pour : {search_queries}",
                "feedback": "La recherche n'a retourné aucun résultat probant. Essayez de reformuler."
            }

        # 4. Vérification croisée & Synthèse (Raisonnement)
        synthesis = self._synthesize(main_query, all_results)
        
        return {
            "search_queries": search_queries,
            "raw_results_count": len(all_results),
            "analysis": synthesis,
            "sources": [res.get('href') for res in all_results[:5]] # Retourner les 5 premiers liens
        }

    def _decompose(self, query: str) -> List[str]:
        """Demander au LLM de décomposer la requête en termes de recherche."""
        system_prompt = (
            "Vous êtes un Stratège en Recherche.\n"
            "Décomposez la demande de l'utilisateur en 3 requêtes ciblées pour un moteur de recherche.\n"
            "Renvoyez une liste JSON de chaînes de caractères."
        )
        try:
            resp = self.llm_client.generate(query, system_prompt=system_prompt, json_mode=True)
            # Basic cleanup
            clean_resp = resp.strip().replace("```json", "").replace("```", "").strip()
            data = json.loads(clean_resp)
            return data if isinstance(data, list) else [query]
        except Exception as e:
            logger.error(f"La décomposition a échoué : {e}")
            return [query]

    def _search(self, query: str) -> List[Dict[str, str]]:
        """Exécuter la recherche en utilisant DuckDuckGo."""
        try:
            with DDGS() as ddgs:
                results = [r for r in ddgs.text(query, max_results=5)]
                return results
        except Exception as e:
            logger.error(f"Erreur de l'outil de recherche : {e}")
            return []

    def _synthesize(self, original_goal: str, results: List[Dict[str, Any]]) -> str:
        """Vérifier les sources et synthétiser la réponse finale."""
        formatted_results = ""
        for i, res in enumerate(results[:10]): # Limiter aux 10 premiers pour les tokens
            formatted_results += f"Source {i+1} ({res.get('href')}):\nTitre: {res.get('title')}\nExtrait: {res.get('body')}\n\n"

        system_prompt = (
            "Vous êtes un Analyste d'Investigation.\n"
            "Tâche : Synthétiser une réponse fiable à partir de multiples sources web.\n"
            "1. Identifiez et soulignez les contradictions entre les sources.\n"
            "2. Notez la fiabilité globale ou les biais si apparents.\n"
            "3. Fournissez une réponse finale claire et structurée.\n"
            "Si des informations manquent ou ne sont pas fiables, dites-le explicitement."
        )
        
        prompt = f"Goal: {original_goal}\n\nWeb Sources Content:\n{formatted_results}"
        
        try:
            return self.llm_client.generate(prompt, system_prompt=system_prompt)
        except Exception as e:
            logger.error(f"La synthèse a échoué : {e}")
            return "Échec de la synthèse des résultats de recherche."
