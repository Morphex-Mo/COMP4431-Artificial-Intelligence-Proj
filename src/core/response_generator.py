"""
Cultural response recommendation module
"""

import openai
from typing import List, Dict
from config.settings import settings
from .cultural_rag import CulturalRAG

class ResponseGenerator:
    def __init__(self):
        openai.api_key = settings.OPENAI_API_KEY
        self.cultural_rag = CulturalRAG()
    
    def generate_responses(self, conversation_context: str, target_culture: str, num_responses: int = 3) -> List[Dict]:
        """
        Generate culturally appropriate response suggestions
        
        Args:
            conversation_context: The conversation history/context
            target_culture: Target culture for responses
            num_responses: Number of response options to generate
        
        Returns:
            List of response dictionaries with text and explanation
        """
        # Get cultural context from RAG
        cultural_context = self.cultural_rag.retrieve_cultural_context(
            conversation_context, target_culture
        )
        
        culture_info = settings.SUPPORTED_CULTURES.get(target_culture, {})
        
        prompt = self._build_response_prompt(
            conversation_context, target_culture, cultural_context, culture_info
        )
        
        try:
            response = openai.ChatCompletion.create(
                model=settings.LLM_MODEL,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300
            )
            
            return self._parse_response_suggestions(response.choices[0].message.content)
        except Exception as e:
            print(f"Response generation error: {e}")
            return self._fallback_responses(target_culture)
    
    def _build_response_prompt(self, context: str, culture: str, cultural_context: List[str], culture_info: Dict) -> str:
        """Build the prompt for response generation"""
        cultural_guidance = "\n".join(cultural_context)
        
        return f"""
        Generate 3 culturally appropriate response suggestions for {culture} culture.
        
        Conversation context: {context}
        
        Cultural guidance:
        {cultural_guidance}
        
        Culture characteristics:
        - Politeness: {culture_info.get('politeness', 'medium')}
        - Directness: {culture_info.get('directness', 'medium')}
        
        Format each response as:
        Response X: [response text]
        Explanation: [why this is culturally appropriate]
        
        """
    
    def _parse_response_suggestions(self, llm_output: str) -> List[Dict]:
        """Parse LLM output into structured response suggestions"""
        responses = []
        lines = llm_output.split('\n')
        
        current_response = {}
        for line in lines:
            if line.startswith('Response'):
                if current_response:
                    responses.append(current_response)
                current_response = {'text': line.split(':', 1)[1].strip()}
            elif line.startswith('Explanation'):
                current_response['explanation'] = line.split(':', 1)[1].strip()
        
        if current_response:
            responses.append(current_response)
        
        return responses
    
    def _fallback_responses(self, culture: str) -> List[Dict]:
        """Provide fallback responses if generation fails"""
        return [
            {
                "text": "Thank you for your message.",
                "explanation": "A safe, polite response appropriate for most cultures"
            }
        ]
