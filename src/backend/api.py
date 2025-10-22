"""
FastAPI backend for CultiTrans
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import io

from src.core.asr import ASRProcessor
from src.core.translator import CulturalTranslator
from src.core.response_generator import ResponseGenerator

app = FastAPI(title="CultiTrans API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
asr_processor = ASRProcessor()
translator = CulturalTranslator()
response_generator = ResponseGenerator()

class TranslationRequest(BaseModel):
    text: str
    source_language: str
    target_culture: str

class TranslationResponse(BaseModel):
    basic_translation: str
    cultural_adaptation: str
    culture_notes: str
    response_suggestions: list

@app.post("/translate", response_model=TranslationResponse)
async def translate_text(request: TranslationRequest):
    """Translate text with cultural awareness"""
    try:
        # Translation
        translation_result = translator.translate_with_culture(
            request.text, request.source_language, request.target_culture
        )
        
        # Response suggestions
        responses = response_generator.generate_responses(
            f"User said: {request.text}", request.target_culture
        )
        
        return TranslationResponse(
            basic_translation=translation_result["basic_translation"],
            cultural_adaptation=translation_result["cultural_adaptation"],
            culture_notes=translation_result["culture_notes"],
            response_suggestions=responses
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/transcribe")
async def transcribe_audio(audio: UploadFile = File(...)):
    """Transcribe audio to text"""
    try:
        audio_data = await audio.read()
        transcription = asr_processor.transcribe_audio(audio_data)
        
        if transcription:
            return {"transcription": transcription}
        else:
            raise HTTPException(status_code=400, detail="Transcription failed")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/cultures")
async def get_supported_cultures():
    """Get list of supported cultures"""
    from config.settings import settings
    return {"cultures": settings.SUPPORTED_CULTURES}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
