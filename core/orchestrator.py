from typing import List, Dict, Any, Optional
import logging
import json
import difflib
from .agent_base import BaseAgent
from .llm_client import GeminiClient
from .observability import get_tracer

logger = logging.getLogger("core.orchestrator")
tracer = get_tracer("core.orchestrator")

class Orchestrator:
    """
    L'Orchestrateur agit comme le cerveau central du système, propulsé par LangGraph.
    """
    
    def __init__(self, llm_client: GeminiClient):
        self.agents: Dict[str, BaseAgent] = {}
        self.llm_client = llm_client
        self.graph = None
        logger.info("Orchestrator initialized with LangGraph support.")

    def register_agent(self, agent: BaseAgent):
        """Enregistrer une nouvelle capacité d'agent."""
        self.agents[agent.name] = agent
        logger.info(f"Agent enregistré : {agent.name} - {agent.description}")

    def _initialize_graph(self):
        """Initialise le graphe LangGraph si nécessaire."""
        if not self.graph:
            from .lang_graph_core import build_graph
            self.graph = build_graph(self.llm_client, self.agents)

    def run(self, user_query: str, status_callback=None) -> Dict[str, Any]:
        """
        Exécute le flux complet en utilisant LangGraph.
        """
        from langchain_core.messages import HumanMessage
        
        self._initialize_graph()
        
        if status_callback:
            status_callback(0, 0, "Orchestrator", "Analyse de votre requête...")

        # Préparation des infos agents pour le planner
        agents_info = "\n".join([f"- {name}: {agent.description}" for name, agent in self.agents.items()])
        
        # Initialisation de l'état (AgentState)
        initial_state = {
            "messages": [HumanMessage(content=user_query)],
            "context": {
                "agents_info": agents_info,
                "pdf_text": user_query # Sera remplacé par le texte réel du PDF si présent
            },
            "plan": [],
            "current_step_idx": 0,
            "results": {"original_query": user_query},
            "errors": [],
            "retry_count": 0
        }

        try:
            # Exécution du graphe (synchrone pour l'instant)
            # Ajout d'une configuration pour la persistance (thread_id)
            config = {"configurable": {"thread_id": "default_user_session"}}
            
            final_state = self.graph.invoke(initial_state, config=config)
            
            # Retourner les résultats formatés pour l'interface existante
            results = final_state.get("results", {})
            
            # Gestion des erreurs dans le résultat final
            if final_state.get("errors"):
                results["erreur"] = "; ".join(final_state["errors"])
            
            if status_callback:
                status_callback(1, 1, "Orchestrator", "Analyse terminée !")
                
            return results
            
        except Exception as e:
            logger.error(f"Échec de l'exécution LangGraph : {e}")
            return {"erreur": f"Erreur d'exécution du graphe : {str(e)}"}
