from typing import Dict, Any, List
import logging
import json
from core.agent_base import BaseAgent
from core.llm_client import OllamaClient

logger = logging.getLogger("agents.reasoning")

class ReasoningAgent(BaseAgent):
    """
    Agent responsable du raisonnement, de la planification et de la décomposition de problèmes.
    """
    
    def __init__(self, llm_client: OllamaClient):
        super().__init__(
            name="ReasoningAgent",
            description="Exécute un raisonnement logique, décompose les problèmes complexes en étapes et crée des plans d'exécution."
        )
        self.llm_client = llm_client

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Raisonner sur un problème.
        
        Clés d'Entrée :
            - context (str) : Le contexte ou la requête sur laquelle raisonner.
            - goal (str) : L'objectif spécifique à atteindre.
            
        Returns :
            - reasoning (str) : La chaîne de pensée (chain of thought).
            - plan (list) : Étapes recommandées.
        """
        self.validate_input(input_data, ["context", "goal"])
        
        context = input_data["context"]
        goal = input_data["goal"]
        
        logger.info(f"Raisonnement sur l'objectif : {goal}")
        
        system_prompt = (
            "Vous êtes un Moteur de Raisonnement Senior.\n"
            "Analysez le contexte et l'objectif.\n"
            "Fournissez une décomposition logique et un plan étape par étape.\n"
            "Renvoyez un JSON avec 'thought_process' (chaîne de caractères) et 'steps' (liste de chaînes de caractères)."
        )
        
        prompt = f"Contexte :\n{context}\n\nObjectif :\n{goal}"
        
        try:
            response = self.llm_client.generate(prompt, system_prompt=system_prompt, json_mode=True)
            
            # Clean response if it contains markdown code blocks
            clean_response = response.strip()
            if clean_response.startswith("```json"):
                clean_response = clean_response[7:]
            if clean_response.startswith("```"):
                clean_response = clean_response[3:]
            if clean_response.endswith("```"):
                clean_response = clean_response[:-3]
            clean_response = clean_response.strip()
            
            return json.loads(clean_response)
        except Exception as e:
            logger.error(f"Le raisonnement a échoué : {e}")
            return {"erreur": str(e)}
