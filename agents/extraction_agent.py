from typing import Dict, Any
import logging
import json
from core.agent_base import BaseAgent
from core.llm_client import OllamaClient

logger = logging.getLogger("agents.extraction")

class ExtractionAgent(BaseAgent):
    """
    Agent responsible for extracting structured data from unstructured text.
    """
    
    def __init__(self, llm_client: OllamaClient):
        super().__init__(
            name="ExtractionAgent",
            description="Extracts structured JSON data from text based on a given schema or instruction."
        )
        self.llm_client = llm_client

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract structured data.
        
        Input Keys:
            - text (str): The source text.
            - fields (list[str]): List of fields to extract.
            
        Returns:
            - extracted_data (dict): The extracted JSON object.
        """
        self.validate_input(input_data, ["text", "fields"])
        
        text = input_data["text"]
        fields = input_data["fields"]
        
        logger.info(f"Extracting fields: {fields}")
        
        system_prompt = (
            "You are a precise data extraction agent.\n"
            f"Extract the following fields: {', '.join(fields)}.\n"
            "Return ONLY a valid JSON object."
        )
        
        prompt = f"Source Text:\n{text[:8000]}"
        
        try:
            response = self.llm_client.generate(prompt, system_prompt=system_prompt, json_mode=True)
            try:
                data = json.loads(response)
                return {"extracted_data": data}
            except json.JSONDecodeError:
                # Fallback: try to find JSON in text if Ollama didn't enforce it perfectly
                logger.warning("Failed to parse JSON directly, returning raw response.")
                return {"extracted_data": {}, "raw_response": response, "error": "JSON Decode Error"}
                
        except Exception as e:
            logger.error(f"Extraction failed: {e}")
            return {"error": str(e)}
