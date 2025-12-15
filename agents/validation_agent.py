from typing import Dict, Any
import logging
from core.agent_base import BaseAgent
from core.llm_client import OllamaClient

logger = logging.getLogger("agents.validator")

class ValidationAgent(BaseAgent):
    """
    Agent responsible for validating the quality and correctness of outputs.
    """
    
    def __init__(self, llm_client: OllamaClient):
        super().__init__(
            name="ValidationAgent",
            description="Validates content against quality criteria and checks for hallucinations or format errors."
        )
        self.llm_client = llm_client

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate content.
        
        Input Keys:
            - content (str): The content to validate.
            - criteria (str): The validation criteria.
            
        Returns:
            - is_valid (bool)
            - feedback (str)
        """
        self.validate_input(input_data, ["content", "criteria"])
        
        content = input_data["content"]
        criteria = input_data["criteria"]
        
        logger.info(f"Validating content against: {criteria}")
        
        system_prompt = (
            "You are a Quality Control Agent.\n"
            "Evaluate the content against the criteria.\n"
            "Return a JSON object with 'is_valid' (boolean) and 'feedback' (string)."
        )
        
        prompt = f"Criteria: {criteria}\n\nContent:\n{content}"
        
        try:
            response = self.llm_client.generate(prompt, system_prompt=system_prompt, json_mode=True)
            import json
            result = json.loads(response)
            return result
        except Exception as e:
            logger.error(f"Validation failed: {e}")
            return {"error": str(e)}
