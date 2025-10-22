"""
Configuration settings for CultiTrans
"""

import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # API Keys
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    GOOGLE_TRANSLATE_API_KEY = os.getenv("GOOGLE_TRANSLATE_API_KEY")
    
    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///cultitrans.db")
    MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017/")
    
    # Model Settings
    WHISPER_MODEL = "base"
    TRANSLATION_MODEL = "facebook/m2m100_418M"
    LLM_MODEL = "gpt-3.5-turbo"
    
    # Cultural Knowledge Base
    CULTURAL_DB_PATH = "data/cultural_knowledge/"
    
    # Supported Languages and Cultures
    SUPPORTED_CULTURES = {
        "japanese": {"language": "ja", "politeness": "high", "directness": "low"},
        "american": {"language": "en", "politeness": "medium", "directness": "high"},
        "chinese": {"language": "zh", "politeness": "high", "directness": "medium"},
        "german": {"language": "de", "politeness": "medium", "directness": "high"},
        "french": {"language": "fr", "politeness": "medium", "directness": "medium"}
    }

settings = Settings()
