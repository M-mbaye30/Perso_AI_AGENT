"""
Configuration centralisée pour l'agent de veille technologique NLP
"""
import os
from dotenv import load_dotenv

# Chargement des variables d'environnement
load_dotenv()

class Config:
    """Configuration globale de l'application"""
    
    # ========================
    # API KEYS
    # ========================
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY non trouvée dans les variables d'environnement")
    
    # ========================
    # CONFIGURATION RECHERCHE
    # ========================
    MAX_SEARCH_RESULTS = int(os.getenv("MAX_SEARCH_RESULTS", "5"))
    SEARCH_TIMEOUT = int(os.getenv("SEARCH_TIMEOUT", "30"))
    
    # ========================
    # MOTS-CLÉS NLP
    # ========================
    NLP_KEYWORDS = [
        # Modèles et architectures
        "transformer models",
        "BERT", "GPT", "T5", "LLaMA",
        "attention mechanism",
        "large language models",
        
        # Tâches NLP
        "natural language processing",
        "machine translation",
        "sentiment analysis", 
        "named entity recognition",
        "text summarization",
        "question answering",
        "text classification",
        "information extraction",
        "text generation",
        "language modeling",
        "speech recognition",
        "dialogue systems",
        "chatbots",
        "text-to-speech",
        "speech-to-text",
        "semantic parsing",
        "text mining",
        "text similarity",
        "text clustering",
        "text embedding",
        "word embeddings",
        "sentence embeddings",
        "contextual embeddings",
        "word2vec", "GloVe", "fastText",
        "Agentic IA"

        
        # Techniques avancées
        "few-shot learning",
        "prompt engineering",
        "fine-tuning",
        "transfer learning",
        "multimodal learning",
        
        # Français
        "traitement automatique des langues",
        "TAL",
        "intelligence artificielle linguistique"
        "Les agents intelligents",
        "agents autonomes",
        "agents conversationnels",
        "agents de veille technologique",
        "agents de recherche",
        "agents d'information",
        "agents d'analyse de données",
        "agents de synthèse",
        "agents de recommandation",
        "agents de surveillance",
    ]
    
    # ========================
    # CONFIGURATION SÉCURITÉ
    # ========================
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", "50000"))
    
    ALLOWED_DOMAINS = [
        "arxiv.org",
        "aclanthology.org", 
        "paperswithcode.com",
        "huggingface.co",
        "towards-datascience.com",
        "medium.com",
        "github.com",
        "openai.com",
        "deepmind.com",
        "ai.googleblog.com"
    ]
    
    # ========================
    # CONFIGURATION STOCKAGE
    # ========================
    DATA_DIR = os.getenv("DATA_DIR", "data")
    REPORTS_DIR = os.getenv("REPORTS_DIR", "reports")
    
    # ========================
    # CONFIGURATION ANALYSE
    # ========================
    RELEVANCE_THRESHOLD = float(os.getenv("RELEVANCE_THRESHOLD", "6.0"))
    MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
    
    # ========================
    # CONFIGURATION LOGGING
    # ========================
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = os.getenv("LOG_FILE", "nlp_agent.log")
    
    # ========================
    # VALIDATION
    # ========================
    @classmethod
    def validate_config(cls) -> bool:
        """Valide la configuration"""
        errors = []
        
        if not cls.OPENAI_API_KEY:
            errors.append("OPENAI_API_KEY manquante")
        
        if cls.MAX_SEARCH_RESULTS <= 0:
            errors.append("MAX_SEARCH_RESULTS doit être > 0")
            
        if cls.RELEVANCE_THRESHOLD < 0 or cls.RELEVANCE_THRESHOLD > 10:
            errors.append("RELEVANCE_THRESHOLD doit être entre 0 et 10")
        
        if errors:
            raise ValueError(f"Erreurs de configuration: {', '.join(errors)}")
        
        return True

# ========================
# INSTANCE GLOBALE
# ========================
# Validation automatique à l'import
Config.validate_config()

# Instance unique à utiliser partout
config = Config()

# Export des constantes principales
NLP_KEYWORDS = config.NLP_KEYWORDS
MAX_SEARCH_RESULTS = config.MAX_SEARCH_RESULTS
DATA_DIR = config.DATA_DIR
REPORTS_DIR = config.REPORTS_DIR