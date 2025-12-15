from typing import List, Dict, Any
import logging
import json
import difflib
from .agent_base import BaseAgent
from .llm_client import OllamaClient

logger = logging.getLogger("core.orchestrator")

class Orchestrator:
    """
    The Orchestrator acts as the central brain.
    """
    
    def __init__(self, llm_client: OllamaClient):
        self.agents: Dict[str, BaseAgent] = {}
        self.llm_client = llm_client
        logger.info("Orchestrator initialized.")

    def register_agent(self, agent: BaseAgent):
        """Register a new agent capability."""
        self.agents[agent.name] = agent
        logger.info(f"Agent registered: {agent.name} - {agent.description}")

    def _get_agent_fuzzy(self, name: str) -> BaseAgent:
        """Find agent with fuzzy matching to handle LLM hallucinations."""
        if name in self.agents:
            return self.agents[name]
        
        # Fuzzy match
        available_names = list(self.agents.keys())
        matches = difflib.get_close_matches(name, available_names, n=1, cutoff=0.6)
        
        if matches:
            best_match = matches[0]
            logger.warning(f"Agent '{name}' not found. Using fuzzy match: '{best_match}'")
            return self.agents[best_match]
        
        return None

    def plan_task(self, user_query: str) -> List[Dict[str, Any]]:
        """
        Use the LLM to create an execution plan.
        """
        agents_info = "\n".join([f"- {name}: {agent.description}" for name, agent in self.agents.items()])
        
        system_prompt = (
            "You are the Orchestrator. Plan the steps to solve the user query.\n"
            "Usage Guidelines:\n"
            "1. Use 'DocumentAnalysisAgent' to summarize or understand text.\n"
            "2. Use 'ReasoningAgent' to make a plan or decision.\n"
            "3. Use 'ExtractionAgent' to get specific JSON fields.\n"
            "4. Use 'ValidationAgent' to check quality.\n\n"
            f"Available Agents:\n{agents_info}\n\n"
            "RESPONSE FORMAT: JSON list of steps.\n"
            "Example:\n"
            '{"steps": [\n'
            '  {"agent": "DocumentAnalysisAgent", "instruction": "Summarize this text", "input_data": "USER_QUERY"},\n'
            '  {"agent": "ExtractionAgent", "instruction": "Extract dates", "input_data": "PREVIOUS_RESULT"}\n'
            ']}'
        )
        
        prompt = f"User Query: {user_query}\n\nCreate a simple plan."
        
        try:
            response = self.llm_client.generate(prompt, system_prompt=system_prompt, json_mode=True)
            plan = json.loads(response)
            return plan.get("steps", [])
        except Exception as e:
            logger.error(f"Failed to plan task: {e}")
            raise

    def run(self, user_query: str) -> Dict[str, Any]:
        """
        Execute the full workflow.
        """
        logger.info(f"Starting execution for query: {user_query}")
        
        try:
            steps = self.plan_task(user_query)
            logger.info(f"Plan created with {len(steps)} steps.")
        except Exception as e:
            return {"error": f"Planning failed: {str(e)}"}

        context = {"original_query": user_query}
        last_result = user_query # Resultat précédent par défaut
        
        for i, step in enumerate(steps):
            agent_name = step.get("agent")
            instruction = step.get("instruction")
            input_source = step.get("input_data", "")
            
            logger.info(f"Step {i+1}: {agent_name} -> {instruction}")
            
            agent = self._get_agent_fuzzy(agent_name)
            if not agent:
                logger.error(f"Agent {agent_name} not found!")
                context[f"step_{i}_error"] = f"Agent {agent_name} not found"
                continue
                
            try:
                # Prepare Input based on Agent Type mapping
                # Automatic wrapping to fix missing keys
                
                # Determine "content" to process
                content_to_process = last_result
                if input_source == "USER_QUERY":
                    content_to_process = user_query
                elif isinstance(last_result, dict):
                    # Try to extract meaningful string content from previous result dict
                    content_to_process = str(last_result)
                    if "analysis" in last_result: content_to_process = last_result["analysis"]
                    if "extracted_data" in last_result: content_to_process = json.dumps(last_result["extracted_data"])

                # Construct Payload
                payload = {
                    "instruction": instruction,
                    "context": context,
                    # Auto-map common keys
                    "text": content_to_process,         # For DocAnalysis, Extraction
                    "content": content_to_process,      # For Validation
                    "goal": instruction,                # For Reasoning
                    "fields": ["summary", "entities"] if "Extraction" in agent.name else [], # Default fields
                    "criteria": instruction             # For Validation
                }

                result = agent.process(payload)
                
                # Store result with agent name for UI display
                context[f"step_{i}_result"] = result
                context[f"step_{i}_agent"] = agent.name  # NEW: Track which agent
                context[agent.name] = result
                
                last_result = result
                
            except Exception as e:
                logger.error(f"Error acting step {i}: {e}")
                context[f"step_{i}_error"] = str(e)
                
        return context
