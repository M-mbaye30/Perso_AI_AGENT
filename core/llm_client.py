import requests
import json
import os
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("core.llm_client")

class OllamaClient:
    """
    Client pour interagir avec une instance locale Ollama OU l'API Gemini.
    Prend en charge le basculement entre Ollama (local) et Gemini (cloud) via une variable d'environnement.
    """
    
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama3"):
        self.use_gemini = os.getenv("USE_GEMINI", "false").lower() == "true"
        
        if self.use_gemini:
            # Gemini configuration
            self.gemini_api_key = os.getenv("GEMINI_API_KEY")
            if not self.gemini_api_key:
                raise ValueError("GEMINI_API_KEY non trouvée dans les variables d'environnement !")
            
            # Nettoyage agressif du nom du modèle (ex: retire 'models/' si présent)
            raw_model = os.getenv("GEMINI_MODEL", "gemini-1.5-flash").strip()
            self.model = raw_model.split("/")[-1] if "/" in raw_model else raw_model
            
            logger.info(f"Utilisation de l'API Gemini ({self.model})")
        else:
            # Configuration Ollama
            self.base_url = os.getenv("OLLAMA_BASE_URL", base_url)
            self.model = os.getenv("OLLAMA_MODEL", model)
            logger.info(f"Utilisation d'Ollama : {self.base_url}, Modèle : {self.model}")

    def generate(self, prompt: str, system_prompt: Optional[str] = None, json_mode: bool = False) -> str:
        """
        Génère une réponse à partir du LLM (Ollama ou Gemini).
        
        Args:
            prompt (str): Le prompt de l'utilisateur.
            system_prompt (Optional[str]): Le prompt système (contexte).
            json_mode (bool): Indique s'il faut forcer une sortie JSON.
            
        Returns:
            str: La réponse textuelle générée.
        """
        if self.use_gemini:
            return self._generate_gemini(prompt, system_prompt)
        else:
            return self._generate_ollama(prompt, system_prompt, json_mode)
    
    def _generate_gemini(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Génère une réponse en utilisant l'API Gemini avec repli automatique exhaustif."""
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.gemini_api_key)
            
            # Liste exhaustive suggérée par l'utilisateur (on s'assure du préfixe 'models/')
            base_models = [
                self.model,
                'gemini-1.5-flash-latest',
                'gemini-1.5-flash',
                'gemini-1.5-pro-latest',
                'gemini-1.5-pro',
                'gemini-pro'
            ]
            
            # Construction de la liste finale avec et sans préfixe, en privilégiant AVEC préfixe
            test_models = []
            for m in base_models:
                if not m: continue
                # On ajoute d'abord la version avec préfixe (recommandé v0.8.5+)
                with_prefix = m if m.startswith("models/") else f"models/{m}"
                if with_prefix not in test_models:
                    test_models.append(with_prefix)
                # On ajoute aussi la version sans préfixe au cas où (fallback)
                without_prefix = m.replace("models/", "")
                if without_prefix not in test_models:
                    test_models.append(without_prefix)
            
            last_exception = None
            for model_name in test_models:
                try:
                    logger.info(f"Tentative Gemini avec : {model_name}")
                    
                    # Déterminer si le modèle supporte system_instruction (v1.5+)
                    # Note: gemini-pro (v1) ne le supporte pas
                    is_legacy = "gemini-pro" in model_name and "1.5" not in model_name
                    
                    if not is_legacy:
                        model = genai.GenerativeModel(
                            model_name=model_name,
                            system_instruction=system_prompt if system_prompt else None
                        )
                        response = model.generate_content(prompt)
                    else:
                        # Fallback pour gemini-pro (v1)
                        model = genai.GenerativeModel(model_name=model_name)
                        full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
                        response = model.generate_content(full_prompt)
                    
                    if response and response.text:
                        return response.text
                except Exception as e:
                    error_msg = str(e)
                    if "404" in error_msg or "not found" in error_msg.lower():
                        logger.warning(f"Modèle {model_name} non trouvé (404). Essai suivant...")
                        last_exception = e
                        continue
                    else:
                        raise e
            
            raise last_exception or RuntimeError("Aucun des modèles Gemini testés n'est accessible.")
            
        except ImportError:
             raise RuntimeError("google-generativeai n'est pas installé.")
        except Exception as e:
            logger.error(f"Erreur fatale Gemini : {e}")
            raise RuntimeError(f"Erreur API Gemini : {e}")
    
    def _generate_ollama(self, prompt: str, system_prompt: Optional[str] = None, json_mode: bool = False) -> str:
        """Génère une réponse en utilisant Ollama."""
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
            logger.debug(f"Envoi de la requête à Ollama : {len(prompt)} caractères")
            response = requests.post(url, json=payload)
            response.raise_for_status()
            
            result = response.json()
            content = result.get("message", {}).get("content", "")
            
            if not content:
                logger.warning("Ollama a renvoyé un contenu vide.")
                
            return content

        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur de communication avec Ollama : {e}")
            raise RuntimeError(f"Erreur API Ollama : {e}")

    def is_available(self) -> bool:
        """Vérifie si le LLM est disponible (Ollama ou Gemini)."""
        if self.use_gemini:
            return bool(self.gemini_api_key)
        else:
            try:
                response = requests.get(f"{self.base_url}")
                return response.status_code == 200
            except:
                return False
