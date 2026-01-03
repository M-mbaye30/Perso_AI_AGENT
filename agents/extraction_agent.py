from typing import Dict, Any
import logging
import json
from core.agent_base import BaseAgent
from core.llm_client import OllamaClient

logger = logging.getLogger("agents.extraction")

class ExtractionAgent(BaseAgent):
    """
    Agent responsable de l'extraction de données structurées à partir de texte non structuré.
    """
    
    def __init__(self, llm_client: OllamaClient):
        super().__init__(
            name="ExtractionAgent",
            description="Extrait des données JSON structurées à partir d'un texte en se basant sur un schéma ou une instruction donnée."
        )
        self.llm_client = llm_client

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extrait des données structurées.
        
        Clés d'Entrée :
            - text (str) : Le texte source.
            - fields (list[str]) : Liste des champs à extraire.
            
        Returns :
            - extracted_data (dict) : L'objet JSON extrait.
        """
        self.validate_input(input_data, ["text", "fields"])
        
        text = input_data["text"]
        fields = input_data["fields"]
        
        logger.info(f"Extraction des champs : {fields}")
        
        system_prompt = (
            "Vous êtes un agent d'extraction de données précis.\n"
            f"Extrayez les champs suivants : {', '.join(fields)}.\n"
            "Renvoyez UNIQUEMENT un objet JSON valide."
        )
        
        prompt = f"Texte Source :\n{text[:8000]}"
        
        try:
            response = self.llm_client.generate(prompt, system_prompt=system_prompt, json_mode=True)
            try:
                data = json.loads(response)
                return {"extracted_data": data}
            except json.JSONDecodeError:
                # Fallback : essayer de trouver du JSON dans le texte si Ollama ne l'a pas forcé parfaitement
                logger.warning("Échec de l'analyse JSON directe, renvoi de la réponse brute.")
                return {"extracted_data": {}, "raw_response": response, "erreur": "Erreur d'Analyse JSON"}
                
        except Exception as e:
            logger.error(f"L'extraction a échoué : {e}")
            return {"erreur": str(e)}
