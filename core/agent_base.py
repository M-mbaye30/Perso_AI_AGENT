from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging

# Configure logger for the core module
logger = logging.getLogger("core.agent")

class BaseAgent(ABC):
    """
    Abstract Base Class for all agents in the architecture.
    """
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.logger = logging.getLogger(f"agent.{name}")
        self.logger.info(f"Agent '{name}' initialized.")

    @abstractmethod
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process the input data and return the result.
        
        Args:
            input_data (Dict[str, Any]): The input payload for the agent.
            
        Returns:
            Dict[str, Any]: The result of the processing.
        """
        pass

    def validate_input(self, input_data: Dict[str, Any], required_keys: list) -> bool:
        """
        Helper to validate that input contains necessary keys.
        """
        missing = [key for key in required_keys if key not in input_data]
        if missing:
            self.logger.warning(f"Missing required keys: {missing}. Attempting to proceed with available data.")
            return False # Indicate missing but don't raise
        return True
