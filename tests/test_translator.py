"""
Tests for cultural translator
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import unittest
from unittest.mock import Mock, patch
from src.core.translator import CulturalTranslator

class TestCulturalTranslator(unittest.TestCase):
    def setUp(self):
        # Mock the translator to avoid dependency issues
        with patch('src.core.translator.Translator'):
            self.translator = CulturalTranslator()
    
    @patch('src.core.translator.Translator')
    def test_basic_translation(self, mock_translator):
        """Test basic translation functionality"""
        # Mock the translation response
        mock_translator.return_value.translate.return_value.text = "こんにちは、元気ですか？"
        
        result = self.translator.translate_with_culture(
            "Hello, how are you?", "en", "japanese"
        )
        
        self.assertIn("basic_translation", result)
        self.assertIn("cultural_adaptation", result)
        self.assertIn("culture_notes", result)
    
    @patch('src.core.translator.Translator')
    def test_cultural_adaptation(self, mock_translator):
        """Test cultural adaptation feature"""
        mock_translator.return_value.translate.return_value.text = "あなたと意見が違います"
        
        result = self.translator.translate_with_culture(
            "I disagree with you", "en", "japanese"
        )
        
        # Japanese adaptation should be more polite
        self.assertTrue(len(result["cultural_adaptation"]) > 0)

if __name__ == "__main__":
    unittest.main()
