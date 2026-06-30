"""
Client IA pour l'orchestrateur.
Utilise LangChain-Google-GenAI pour une intégration native avec Phoenix.
Modèle : gemini-2.0-flash-lite (le moins coûteux disponible).
"""
import os
import logging
from typing import Optional
import streamlit as st

logger = logging.getLogger("core.llm_client")
logger.setLevel(logging.INFO)

# Modèle par défaut
DEFAULT_MODEL = "gemini-3.5-flash"

class GeminiClient:
    """Client LangChain pour Gemini avec tracking natif des tokens."""
    
    def __init__(self, model=DEFAULT_MODEL):
        self.model = model
        self.llm = None
        
        # Récupération de la clé Gemini (priorité : secrets Streamlit > env)
        self.gemini_api_key = None
        
        # Tentative pour les secrets Streamlit
        try:
            if hasattr(st, "secrets") and "GEMINI_API_KEY" in st.secrets:
                self.gemini_api_key = st.secrets["GEMINI_API_KEY"].strip()
        except:
            pass
            
        # Repli sur les variables d'environnement
        if not self.gemini_api_key:
            env_key = os.getenv("GEMINI_API_KEY")
            if env_key:
                self.gemini_api_key = env_key.strip()

        if not self.gemini_api_key:
            logger.error("AUCUNE CLÉ GEMINI TROUVÉE DANS .env OU SECRETS")
        else:
            self._init_llm()
    
    def _init_llm(self):
        """Initialise le modèle LangChain."""
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            
            self.llm = ChatGoogleGenerativeAI(
                model=self.model,
                google_api_key=self.gemini_api_key,
                temperature=0.7
            )
            logger.info(f"LangChain Gemini initialisé avec le modèle {self.model}")
        except ImportError:
            logger.error("langchain-google-genai n'est pas installé")
        except Exception as e:
            logger.error(f"Erreur initialisation LangChain Gemini: {e}")

    def is_available(self) -> bool:
        """Vérifie si le client est prêt."""
        return self.llm is not None

    def generate(self, prompt: str, system_prompt: Optional[str] = None, json_mode: bool = False) -> str:
        """Génère une réponse en utilisant LangChain-Gemini."""
        if not self.llm:
            raise RuntimeError("Le client LangChain Gemini n'est pas initialisé")
        
        try:
            from langchain_core.messages import HumanMessage, SystemMessage
            
            messages = []
            
            # System prompt
            if system_prompt:
                messages.append(SystemMessage(content=system_prompt))
            
            # User prompt
            messages.append(HumanMessage(content=prompt))
            
            # Générer la réponse (les tokens sont automatiquement trackés par Phoenix)
            response = self.llm.invoke(messages)
            
            if response and response.content:
                content = response.content
                if isinstance(content, list):
                    text_parts = []
                    for part in content:
                        if isinstance(part, dict) and 'text' in part:
                            text_parts.append(part['text'])
                        elif isinstance(part, str):
                            text_parts.append(part)
                    return "".join(text_parts)
                elif isinstance(content, str):
                    return content
                else:
                    return str(content)
            
            raise RuntimeError("Réponse vide du modèle Gemini")

        except Exception as e:
            logger.error(f"Erreur API Gemini : {e}")
            raise RuntimeError(f"Erreur API Gemini : {e}")

# Alias pour la compatibilité temporaire des agents
OllamaClient = GeminiClient
