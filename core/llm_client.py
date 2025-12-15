import requests
import json
import os
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("core.llm_client")

class OllamaClient:
    """
    Client for interacting with a local Ollama instance.
    """
    
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama3"):
        self.base_url = os.getenv("OLLAMA_BASE_URL", base_url)
        self.model = os.getenv("OLLAMA_MODEL", model)
        logger.info(f"OllamaClient initialized with URL: {self.base_url}, Model: {self.model}")

    def generate(self, prompt: str, system_prompt: Optional[str] = None, json_mode: bool = False) -> str:
        """
        Generate a response from the LLM.
        
        Args:
            prompt (str): The user prompt.
            system_prompt (Optional[str]): The system prompt (context).
            json_mode (bool): Whether to enforce JSON output (Ollama feature).
            
        Returns:
            str: The generated text response.
        """
        url = f"{self.base_url}/api/chat"
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False
        }
        
        if json_mode:
            payload["format"] = "json"

        try:
            logger.debug(f"Sending request to Ollama: {len(prompt)} chars")
            response = requests.post(url, json=payload)
            response.raise_for_status()
            
            result = response.json()
            content = result.get("message", {}).get("content", "")
            
            if not content:
                logger.warning("Ollama returned empty content.")
                
            return content

        except requests.exceptions.RequestException as e:
            logger.error(f"Error communicating with Ollama: {e}")
            raise RuntimeError(f"Ollama API Error: {e}")

    def is_available(self) -> bool:
        """Check if Ollama is running."""
        try:
            response = requests.get(f"{self.base_url}")
            return response.status_code == 200
        except:
            return False
