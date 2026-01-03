from typing import Dict, Any
import logging
from core.agent_base import BaseAgent
from core.llm_client import OllamaClient

logger = logging.getLogger("agents.doc_analysis")

class DocumentAnalysisAgent(BaseAgent):
    """
    Agent responsable de l'analyse de documents (résumé, extraction d'informations clés).
    """
    
    def __init__(self, llm_client: OllamaClient):
        super().__init__(
            name="DocumentAnalysisAgent",
            description="Analyse les documents textuels pour fournir des résumés et extraire les thèmes clés."
        )
        self.llm_client = llm_client

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Traite le texte d'un document.
        
        Clés d'Entrée :
            - text (str) : Le contenu du document.
            - task (str) : Instruction spécifique optionnelle (ex : "résumer", "extraire_dates"). Par défaut "résumer".
            
        Returns :
            - analysis (str) : Le texte de résultat.
        """
        self.validate_input(input_data, ["text"])
        
        text = input_data["text"]
        # Prend en charge à la fois 'task' (interne) et 'instruction' (depuis l'Orchestrateur)
        task = input_data.get("instruction") or input_data.get("task", "résumer")
        
        logger.info(f"Traitement de la tâche d'analyse documentaire : {task}")
        
        # Auto-détection du chat si la tâche est générique mais que le texte est court et ressemble à une question
        if task in ["summarize", "résumer"] and len(text) < 200 and "?" in text:
             task = "chat_response"

        if task in ["summarize", "résumer"]:
            prompt = f"Veuillez fournir un résumé concis du document suivant :\n\n{text[:10000]}..." # Tronquer par sécurité
        elif task == "chat_response" or "répondre" in task.lower() or "chat" in task.lower() or "answer" in task.lower():
             prompt = (
                 "Tu es 'Agentic AI Orchestrator', un système intelligent multi-agents développé pour l'analyse de documents et l'automatisation de tâches. "
                 "Tu utilises plusieurs agents spécialisés : Analyse Documentaire, Raisonnement, Extraction et Validation. "
                 "Réponds de manière concise et professionnelle.\n\n"
                 f"Question de l'utilisateur :\n{text[:2000]}"
             )
        else:
            # Transmettre l'instruction brute directement au LLM
            prompt = f"Suivez attentivement cette instruction : {task}\n\nDocument :\n{text[:10000]}..."

        try:
            response = self.llm_client.generate(prompt)
            return {"analysis": response}
        except Exception as e:
            logger.error(f"L'analyse a échoué : {e}")
            return {"erreur": str(e)}
