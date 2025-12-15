from typing import Dict, Any, List
import logging
import json
from core.agent_base import BaseAgent
from core.llm_client import OllamaClient

logger = logging.getLogger("agents.reasoning")

class ReasoningAgent(BaseAgent):
    """
    Agent responsible for reasoning, planning, and problem decomposition.
    """
    
    def __init__(self, llm_client: OllamaClient):
        super().__init__(
            name="ReasoningAgent",
            description="Performs logical reasoning, breaks down complex problems into steps, and creates execution plans."
        )
        self.llm_client = llm_client

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Reason about a problem.
        
        Input Keys:
            - context (str): The context or query to reason about.
            - goal (str): The specific goal to achieve.
            
        Returns:
            - reasoning (str): The chain of thought.
            - plan (list): Recommended steps.
        """
        self.validate_input(input_data, ["context", "goal"])
        
        context = input_data["context"]
        goal = input_data["goal"]
        
        logger.info(f"Reasoning about goal: {goal}")
        
        system_prompt = (
            "You are a Senior Reasoning Engine.\n"
            "Analyze the context and goal.\n"
            "Provide a logical breakdown and a step-by-step plan.\n"
            "Return JSON with 'thought_process' (string) and 'steps' (list of strings)."
        )
        
        prompt = f"Context:\n{context}\n\nGoal:\n{goal}"
        
        try:
            response = self.llm_client.generate(prompt, system_prompt=system_prompt, json_mode=True)
            return json.loads(response)
        except Exception as e:
            logger.error(f"Reasoning failed: {e}")
            return {"error": str(e)}
