from typing import Dict, Any
import logging
from core.agent_base import BaseAgent
from core.llm_client import OllamaClient

logger = logging.getLogger("agents.doc_analysis")

class DocumentAnalysisAgent(BaseAgent):
    """
    Agent responsible for analyzing documents (summarization, key info extraction).
    """
    
    def __init__(self, llm_client: OllamaClient):
        super().__init__(
            name="DocumentAnalysisAgent",
            description="Analyzes text documents to provide summaries and extract key topics."
        )
        self.llm_client = llm_client

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a document text.
        
        Input Keys:
            - text (str): The content of the document.
            - task (str): Optional specific instruction (e.g. "summarize", "extract_dates"). default "summarize"
            
        Returns:
            - analysis (str): The result text.
        """
        self.validate_input(input_data, ["text"])
        
        text = input_data["text"]
        task = input_data.get("task", "summarize")
        
        logger.info(f"Processing document analysis task: {task}")
        
        if task == "summarize":
            prompt = f"Please provide a concise summary of the following document:\n\n{text[:10000]}..." # Truncate for safety
        else:
            prompt = f"Analyze the following document based on this instruction: {task}\n\nDocument:\n{text[:10000]}..."

        try:
            response = self.llm_client.generate(prompt)
            return {"analysis": response}
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            return {"error": str(e)}
