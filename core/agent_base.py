from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging

# Configuration du logger pour le module core
logger = logging.getLogger("core.agent")

class BaseAgent(ABC):
    """
    Classe de base abstraite pour tous les agents de l'architecture.
    """
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.logger = logging.getLogger(f"agent.{name}")
        self.logger.info(f"Agent '{name}' initialisé.")

    @abstractmethod
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Traite les données d'entrée et renvoie le résultat.
        
        Args:
            input_data (Dict[str, Any]) : Le payload d'entrée pour l'agent.
            
        Returns:
            Dict[str, Any] : Le résultat du traitement.
        """
        pass

    def validate_input(self, input_data: Dict[str, Any], required_keys: list) -> bool:
        """
        Utilitaire pour valider que l'entrée contient les clés nécessaires.
        """
        missing = [key for key in required_keys if key not in input_data]
        if missing:
            self.logger.warning(f"Clés requises manquantes : {missing}. Tentative de poursuite avec les données disponibles.")
            return False # Indique une absence de clé mais ne lève pas d'exception
        return True
