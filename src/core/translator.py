"""
Cultural-aware translation module
"""

from transformers import M2M100ForConditionalGeneration, M2M100Tokenizer
from googletrans import Translator
from typing import Dict, Any
import openai
from config.settings import settings

class CulturalTranslator:
    def __init__(self):
        self.google_translator = Translator()
        self.m2m_model = M2M100ForConditionalGeneration.from_pretrained(settings.TRANSLATION_MODEL)
        self.m2m_tokenizer = M2M100Tokenizer.from_pretrained(settings.TRANSLATION_MODEL)
        openai.api_key = settings.OPENAI_API_KEY
    
    def translate_with_culture(self, text: str, source_lang: str, target_culture: str) -> Dict[str, Any]:
        """
        Translate text with cultural context awareness
        
        Args:
            text: Input text to translate
            source_lang: Source language code
            target_culture: Target culture key
        
        Returns:
            Dictionary with translation and cultural suggestions
        """
        culture_info = settings.SUPPORTED_CULTURES.get(target_culture, {})
        target_lang = culture_info.get("language", "en")
        
        # Basic translation
        basic_translation = self._translate_text(text, source_lang, target_lang)
        
        # Cultural adaptation
        cultural_adaptation = self._adapt_culturally(
            basic_translation, target_culture, culture_info
        )
        
        return {
            "basic_translation": basic_translation,
            "cultural_adaptation": cultural_adaptation,
            "culture_notes": self._get_culture_notes(target_culture),
            "confidence": 0.85  # Placeholder
        }
    
    def _translate_text(self, text: str, source_lang: str, target_lang: str) -> str:
        """Basic translation using Google Translate"""
        try:
            result = self.google_translator.translate(text, src=source_lang, dest=target_lang)
            return result.text
        except:
            return text  # Fallback
    
    def _adapt_culturally(self, text: str, culture: str, culture_info: Dict) -> str:
        """Adapt translation based on cultural context using LLM"""
        politeness = culture_info.get("politeness", "medium")
        directness = culture_info.get("directness", "medium")
        
        prompt = f"""
        Adapt the following text for {culture} culture:
        Original: "{text}"
        
        Cultural guidelines:
        - Politeness level: {politeness}
        - Directness level: {directness}
        
        Provide a culturally appropriate version:
        """
        
        try:
            response = openai.ChatCompletion.create(
                model=settings.LLM_MODEL,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150
            )
            return response.choices[0].message.content.strip()
        except:
            return text  # Fallback
    
    def _get_culture_notes(self, culture: str) -> str:
        """Get cultural notes for the target culture"""
        notes = {
            "japanese": "Use polite language and indirect expressions",
            "american": "Be direct and confident in communication",
            "chinese": "Show respect and avoid confrontational language",
            "german": "Be precise and straightforward",
            "french": "Maintain elegance and proper etiquette"
        }
        return notes.get(culture, "Be respectful and appropriate")
