from typing import Dict, Any
import logging
from core.agent_base import BaseAgent
from core.llm_client import OllamaClient

logger = logging.getLogger("agents.validator")

class ValidationAgent(BaseAgent):
    """
    Agent responsable de la validation de la qualité et de l'exactitude des sorties.
    """
    
    def __init__(self, llm_client: OllamaClient):
        super().__init__(
            name="ValidationAgent",
            description="Valide le contenu par rapport à des critères de qualité et vérifie l'absence d'hallucinations ou d'erreurs de format."
        )
        self.llm_client = llm_client

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Valider le contenu.
        
        Clés d'Entrée :
            - content (str) : Le contenu à valider.
            - criteria (str) : Les critères de validation.
            
        Returns :
            - is_valid (bool)
            - feedback (str)
        """
        self.validate_input(input_data, ["content", "criteria"])
        
        content = input_data["content"]
        criteria = input_data["criteria"]
        
        logger.info(f"Validation du contenu par rapport à : {criteria}")
        
        system_prompt = (
            "Vous êtes un Agent de Contrôle Qualité.\n"
            "Évaluez le contenu par rapport aux critères fournis.\n"
            "Renvoyez un objet JSON avec 'is_valid' (booléen) et 'feedback' (chaîne de caractères)."
        )
        
        prompt = f"Critères : {criteria}\n\nContenu :\n{content}"
        
        try:
            response = self.llm_client.generate(prompt, system_prompt=system_prompt, json_mode=True)
            import json
            
            # Clean response if it contains markdown code blocks
            clean_response = response.strip()
            if clean_response.startswith("```json"):
                clean_response = clean_response[7:]
            if clean_response.startswith("```"):
                clean_response = clean_response[3:]
            if clean_response.endswith("```"):
                clean_response = clean_response[:-3]
            clean_response = clean_response.strip()

            result = json.loads(clean_response)
            return result
        except Exception as e:
            logger.error(f"La validation a échoué : {e}")
            return {"erreur": str(e)}
