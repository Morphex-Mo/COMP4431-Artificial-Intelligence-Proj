"""
Streamlit frontend application
"""

try:
    import streamlit as st
except Exception as e:
    raise RuntimeError(
        "Missing required dependency 'streamlit'. Please install it with "
        "'pip install streamlit' and restart the application."
    ) from e

import io
from src.core.asr import ASRProcessor
from src.core.translator import CulturalTranslator
from src.core.response_generator import ResponseGenerator
from config.settings import settings

def main():
    st.set_page_config(
        page_title="CultiTrans",
        page_icon="🌍",
        layout="wide"
    )
    
    st.title("🌍 CultiTrans: Cultural Translation Assistant")
    st.markdown("**Bridging languages and cultures with AI**")
    
    # Initialize components
    if 'asr' not in st.session_state:
        st.session_state.asr = ASRProcessor()
        st.session_state.translator = CulturalTranslator()
        st.session_state.response_gen = ResponseGenerator()
        st.session_state.conversation_history = []
    
    # Sidebar for settings
    with st.sidebar:
        st.header("Settings")
        source_lang = st.selectbox("Source Language", ["en", "zh", "ja", "de", "fr"])
        target_culture = st.selectbox(
            "Target Culture", 
            list(settings.SUPPORTED_CULTURES.keys())
        )
        
        st.header("Cultural Info")
        culture_info = settings.SUPPORTED_CULTURES.get(target_culture, {})
        st.info(f"**Language:** {culture_info.get('language', 'N/A')}")
        st.info(f"**Politeness Level:** {culture_info.get('politeness', 'N/A')}")
        st.info(f"**Directness Level:** {culture_info.get('directness', 'N/A')}")
    
    # Main interface
    col1, col2 = st.columns(2)
    
    with col1:
        st.header("Input")
        
        # Text input
        user_text = st.text_area("Enter text to translate:", height=100)
        
        # Audio input
        st.subheader("Or record audio:")
        audio_file = st.file_uploader("Upload audio file", type=['wav', 'mp3', 'ogg'])
        
        if audio_file:
            st.audio(audio_file)
            if st.button("Transcribe Audio"):
                audio_bytes = audio_file.read()
                transcribed_text = st.session_state.asr.transcribe_audio(audio_bytes)
                if transcribed_text:
                    user_text = transcribed_text
                    st.success(f"Transcribed: {transcribed_text}")
        
        if st.button("Translate & Get Cultural Suggestions") and user_text:
            process_translation(user_text, source_lang, target_culture)
    
    with col2:
        st.header("Results")
        
        if 'translation_result' in st.session_state:
            result = st.session_state.translation_result
            
            st.subheader("Translation")
            st.write(f"**Basic:** {result['basic_translation']}")
            st.write(f"**Cultural Adaptation:** {result['cultural_adaptation']}")
            
            st.subheader("Cultural Notes")
            st.info(result['culture_notes'])
            
            st.subheader("Response Suggestions")
            if 'response_suggestions' in st.session_state:
                for i, resp in enumerate(st.session_state.response_suggestions, 1):
                    with st.expander(f"Response Option {i}"):
                        st.write(f"**Text:** {resp['text']}")
                        st.write(f"**Explanation:** {resp['explanation']}")
    
    # Conversation history
    if st.session_state.conversation_history:
        st.header("Conversation History")
        for item in st.session_state.conversation_history[-5:]:  # Show last 5
            st.text(f"[{item['timestamp']}] {item['source']} → {item['target']}")

def process_translation(text: str, source_lang: str, target_culture: str):
    """Process translation and generate cultural suggestions"""
    with st.spinner("Translating and analyzing cultural context..."):
        # Translation
        translation_result = st.session_state.translator.translate_with_culture(
            text, source_lang, target_culture
        )
        st.session_state.translation_result = translation_result
        
        # Response suggestions
        response_suggestions = st.session_state.response_gen.generate_responses(
            f"User said: {text}\nTranslation: {translation_result['cultural_adaptation']}", 
            target_culture
        )
        st.session_state.response_suggestions = response_suggestions
        
        # Add to conversation history
        import datetime
        st.session_state.conversation_history.append({
            'timestamp': datetime.datetime.now().strftime("%H:%M"),
            'source': text,
            'target': translation_result['cultural_adaptation']
        })

if __name__ == "__main__":
    main()
