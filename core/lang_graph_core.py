from typing import TypedDict, Annotated, List, Dict, Any, Union, Literal
from langgraph.graph import StateGraph, END, START
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
import logging
import json

logger = logging.getLogger("core.lang_graph")

class AgentState(TypedDict):
    """
    État du graphe LangGraph.
    Représente la 'mémoire vive' de la conversation et du processus de réflexion.
    """
    messages: Annotated[List[BaseMessage], add_messages]
    context: Dict[str, Any]
    plan: List[Dict[str, Any]]
    current_step_idx: int
    results: Dict[str, Any]
    errors: List[str]
    retry_count: int

from langgraph.checkpoint.memory import MemorySaver

import sqlite3

def get_planner_node(llm_client):
    """Crée le nœud de planification avec conscience de l'historique."""
    
    # Patterns pour les requêtes simples (pas besoin d'agents)
    SIMPLE_PATTERNS = [
        "bonjour", "salut", "hello", "hi", "coucou", "bonsoir",
        "merci", "thanks", "au revoir", "bye", "à bientôt",
        "comment vas-tu", "ça va", "comment tu vas",
        "qui es-tu", "tu es qui", "présente-toi", "c'est quoi ton nom"
    ]
    
    def is_simple_query(query: str) -> bool:
        """Détecte si la requête est simple (pas besoin d'agents)."""
        query_lower = query.lower().strip()
        # Salutations et questions basiques
        for pattern in SIMPLE_PATTERNS:
            if pattern in query_lower:
                return True
        # Très courte requête (moins de 5 mots)
        if len(query_lower.split()) <= 3:
            return True
        return False
    
    def planner(state: AgentState):
        user_query = state["results"]["original_query"]
        
        # OPTIMISATION: Réponse directe pour requêtes simples
        if is_simple_query(user_query):
            logger.info(f"[OPTIMISATION] Requête simple détectée, réponse directe")
            try:
                response = llm_client.generate(
                    user_query,
                    system_prompt=(
                        "Tu es l'Agent IA Orchestrateur, un assistant intelligent multi-agents. "
                        "Tu as été développé pour orchestrer différents agents spécialisés "
                        "(recherche web, analyse de documents, raisonnement). "
                        "Réponds de manière concise, amicale et professionnelle en français."
                    )
                )
                return {
                    "plan": [],  # Pas d'agents à appeler
                    "results": {**state["results"], "direct_response": response}
                }
            except Exception as e:
                logger.error(f"Erreur réponse directe: {e}")
        
        # Requête complexe : planification normale
        history = ""
        if len(state["messages"]) > 1:
            history = "\nHistorique :\n" + "\n".join([f"{type(m).__name__}: {m.content}" for m in state["messages"][:-1]])
            
        agents_info = state["context"].get("agents_info", "")
        
        system_prompt = (
            "Vous êtes l'Orchestrateur. Planifiez les étapes pour résoudre la requête.\n"
            "IMPORTANT: N'appelez des agents QUE si vraiment nécessaire.\n"
            "- Pour les recherches web : WebSearchAgent\n"
            "- Pour l'analyse de documents : DocumentAnalysisAgent\n"
            "- Pour le raisonnement complexe : ReasoningAgent\n"
            "FORMAT : {\"steps\": [{\"agent\": \"AgentName\", \"instruction\": \"...\"}]}\n"
            "Si aucun agent n'est nécessaire, retournez {\"steps\": []}"
        )
        prompt = f"Agents Disponibles :\n{agents_info}\n{history}\n\nRequête : {user_query}"
        
        try:
            response = llm_client.generate(prompt, system_prompt=system_prompt, json_mode=True)
            clean_res = response.strip().replace("```json", "").replace("```", "").strip()
            plan_data = json.loads(clean_res)
            steps = plan_data.get("steps", [])
            
            # Si le planificateur décide qu'aucune étape/agent n'est requis
            if not steps:
                logger.info("Planner decided no agents are needed. Generating direct response...")
                direct_resp = llm_client.generate(
                    user_query,
                    system_prompt=(
                        "Tu es l'Agent IA Orchestrateur, un assistant intelligent multi-agents. "
                        "Tu as été développé pour orchestrer différents agents spécialisés "
                        "(recherche web, analyse de documents, raisonnement). "
                        "Réponds à la question de l'utilisateur directement et de manière complète et professionnelle en français."
                    )
                )
                return {
                    "plan": [],
                    "results": {**state["results"], "direct_response": direct_resp}
                }
            
            return {"plan": steps}
        except Exception as e:
            logger.error(f"Erreur Planification: {e}")
            try:
                logger.info("Planification failed. Falling back to direct response...")
                direct_resp = llm_client.generate(
                    user_query,
                    system_prompt=(
                        "Tu es l'Agent IA Orchestrateur, un assistant intelligent multi-agents. "
                        "Réponds directement à la question de l'utilisateur de manière concise et professionnelle en français."
                    )
                )
                return {
                    "plan": [],
                    "results": {**state["results"], "direct_response": direct_resp}
                }
            except Exception as e_inner:
                logger.error(f"Erreur Fallback direct: {e_inner}")
                return {"errors": [f"Planification failed: {str(e)}", f"Fallback failed: {str(e_inner)}"]}
            
    return planner

def router_node(state: AgentState) -> Literal["call_agent", "end_process", "error_node"]:
    """Décide de la prochaine étape du graphe."""
    if state.get("errors"):
        return "error_node"
        
    if state["current_step_idx"] < len(state["plan"]):
        return "call_agent"
    
    return "end_process"

def build_graph(llm_client, agents_registry):
    """Construit et compile le graphe LangGraph."""
    workflow = StateGraph(AgentState)
    
    # 1. Ajouter le Planner
    workflow.add_node("planner", get_planner_node(llm_client))
    
    # 2. Ajouter les agents comme nœuds
    for agent_name, agent in agents_registry.items():
        workflow.add_node(agent_name, agent.as_node)
        
    # 3. Nœud de routage/exécution par défaut
    def agent_executor(state: AgentState):
        """Détermine quel agent appeler selon le plan."""
        step = state["plan"][state["current_step_idx"]]
        return step["agent"]
    
    # Construction du flux
    workflow.add_edge(START, "planner")
    
    # Transition conditionnelle après le planner
    workflow.add_conditional_edges(
        "planner",
        router_node,
        {
            "call_agent": "executor_router",
            "end_process": END,
            "error_node": END # Pour simplifier au début
        }
    )
    
    # Le router d'exécution branche vers les agents
    workflow.add_node("executor_router", lambda x: x) # Nœud passe-plat
    workflow.add_conditional_edges(
        "executor_router",
        lambda state: state["plan"][state["current_step_idx"]]["agent"],
        {name: name for name in agents_registry.keys()}
    )
    
    # Chaque agent retourne vers le router pour l'étape suivante
    for agent_name in agents_registry.keys():
        workflow.add_edge(agent_name, "planner_router_check")
        
    # Petit nœud pour boucler
    workflow.add_node("planner_router_check", lambda x: x)
    workflow.add_conditional_edges(
        "planner_router_check",
        router_node,
        {
            "call_agent": "executor_router",
            "end_process": END,
            "error_node": END
        }
    )
    
    # Persistance - Utilisation de MemorySaver pour compatibilité
    # Note: SqliteSaver nécessite une version compatible de langgraph-checkpoint
    memory = MemorySaver()
    
    return workflow.compile(checkpointer=memory)
