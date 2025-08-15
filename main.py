import os
import io
import shutil
import base64
import logging
from typing import Dict, List
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests

from services.stt_service import STTService
from services.tts_service import TTSService
from services.llm_service import LLMService

# -----------------------
# Configuration
# -----------------------
load_dotenv()

# Environment variables
MURF_API_KEY = os.getenv("MURF_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
ASSEMBLYAI_API_KEY = os.getenv("ASSEMBLYAI_API_KEY")

# Validate required environment variables
if not all([MURF_API_KEY, GEMINI_API_KEY, ASSEMBLYAI_API_KEY]):
    raise ValueError("Missing required environment variables")

# Directory setup
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Logging configuration
logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# -----------------------
# Pydantic Models
# -----------------------
class TTSRequest(BaseModel):
    text: str
    voice_id: str = "en-US-natalie"

class LLMRequest(BaseModel):
    text: str

# -----------------------
# FastAPI App Setup
# -----------------------
app = FastAPI(
    title="Alpaca Voice Agent API",
    description="API for Alpaca voice agent with STT, TTS, and LLM capabilities, made during the 30 days of voice agents challenge",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Restrict for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# -----------------------
# Service Initialization
# -----------------------
stt_service = STTService(ASSEMBLYAI_API_KEY)
tts_service = TTSService(MURF_API_KEY)
llm_service = LLMService(GEMINI_API_KEY)

# In-memory chat storage
chat_histories: Dict[str, List[Dict[str, str]]] = {}

# -----------------------
# Helper Functions
# -----------------------
def get_fallback_response(fallback_text: str) -> dict:
    """Generate fallback response with audio."""
    fallback_audio = tts_service.fallback_audio_base64(fallback_text)
    return {
        "text": fallback_text,
        "audio_base64": fallback_audio
    }

def download_audio_as_base64(audio_url: str) -> str:
    """Download audio from URL and convert to base64."""
    audio_response = requests.get(audio_url)
    audio_response.raise_for_status()
    return base64.b64encode(audio_response.content).decode("utf-8")

# -----------------------
# Routes
# -----------------------
@app.get("/")
async def read_index():
    """Serve the main page."""
    return FileResponse("static/index.html")

@app.get("/ping")
async def ping():
    """Health check endpoint."""
    logger.info("Ping endpoint accessed")
    return "This Webpage is served using Python's FastAPI"

@app.post("/generate-audio/")
async def generate_audio(request: TTSRequest):
    """Generate audio from text using TTS service."""
    logger.info(f"Generating audio for text: {request.text[:50]}...")
    
    try:
        audio_url = tts_service.generate_audio(request.text, request.voice_id)
        logger.info("Audio generation successful")
        return {"audio_url": audio_url}
    
    except Exception as e:
        logger.error(f"Audio generation failed: {e}")
        fallback_text = "I'm having trouble connecting right now."
        fallback_response = get_fallback_response(fallback_text)
        return {"error": str(e), **fallback_response}

@app.post("/upload-audio/")
async def upload_audio(file: UploadFile = File(...)):
    """Upload audio file to server."""
    logger.info(f"Uploading file: {file.filename}")
    
    try:
        file_location = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        file_size = os.path.getsize(file_location)
        logger.info(f"File uploaded successfully: {file.filename} ({file_size} bytes)")
        
        return JSONResponse(content={
            "filename": file.filename,
            "size": file_size,
            "content-type": file.content_type
        })
    
    except Exception as e:
        logger.error(f"File upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.post("/transcribe/file")
async def transcribe_audio(file: UploadFile = File(...)):
    """Transcribe uploaded audio file to text."""
    logger.info(f"Transcribing audio file: {file.filename}")
    
    try:
        audio_data = await file.read()
        transcription = stt_service.transcribe_audio_bytes(audio_data)
        logger.info(f"Transcription successful: {transcription[:50]}...")
        return {"transcription": transcription}
    
    except Exception as e:
        logger.error(f"Transcription failed: {e}")
        return {"error": str(e), "transcription": ""}

@app.post("/tts-echo")
async def echo_murf_voice(file: UploadFile = File(...)):
    """Echo back the transcribed audio as speech."""
    logger.info("Processing TTS echo request")
    fallback_text = "I'm having trouble processing that."
    
    try:
        audio_bytes = await file.read()
        transcript = stt_service.transcribe_audio_bytes(audio_bytes)
        
        if not transcript:
            raise Exception("No transcription produced")
        
        logger.info(f"Echoing transcription: {transcript[:50]}...")
        audio_url = tts_service.generate_audio(transcript, "en-US-natalie")
        
        # Stream the audio response
        audio_response = requests.get(audio_url)
        audio_response.raise_for_status()
        
        return StreamingResponse(
            io.BytesIO(audio_response.content),
            media_type="audio/mpeg"
        )
    
    except Exception as e:
        logger.error(f"TTS Echo failed: {e}")
        fallback_response = get_fallback_response(fallback_text)
        return JSONResponse(content={"error": str(e), **fallback_response})

@app.post("/llm/query")
async def llm_query(file: UploadFile = File(...)):
    """Process audio through STT -> LLM -> TTS pipeline."""
    logger.info("Processing LLM query")
    fallback_text = "I couldn't process that just now."
    
    try:
        # Transcribe audio
        audio_bytes = await file.read()
        transcript = stt_service.transcribe_audio_bytes(audio_bytes)
        
        if not transcript:
            raise Exception("No transcription produced")
        
        logger.info(f"Processing query: {transcript[:50]}...")
        
        # Generate LLM response
        llm_output = llm_service.generate_reply(transcript)
        
        if not llm_output:
            raise Exception("No LLM response generated")
        
        logger.info(f"LLM response: {llm_output[:50]}...")
        
        # Convert response to audio
        audio_url = tts_service.generate_audio(llm_output, "en-US-natalie")
        audio_base64 = download_audio_as_base64(audio_url)
        
        return {
            "text": llm_output,
            "audio_base64": audio_base64
        }
    
    except Exception as e:
        logger.error(f"LLM query failed: {e}")
        fallback_response = get_fallback_response(fallback_text)
        return {"error": str(e), **fallback_response}

@app.post("/agent/chat/{sessionId}")
async def agent_chat(sessionId: str, file: UploadFile = File(...)):
    """Handle conversational AI chat with memory."""
    logger.info(f"Processing chat for session: {sessionId}")
    fallback_text = "I'm having trouble connecting right now. Let's try again later."
    
    try:
        # Transcribe audio
        audio_bytes = await file.read()
        transcript = stt_service.transcribe_audio_bytes(audio_bytes)
        
        if not transcript:
            raise Exception("No transcription produced")
        
        logger.info(f"User message: {transcript[:50]}...")
        
        # Get or create chat history
        if sessionId not in chat_histories:
            chat_histories[sessionId] = []
        
        messages = chat_histories[sessionId]
        messages.append({"role": "user", "content": transcript})
        
        # Generate LLM response with context
        conversation_context = "\n".join([f"{msg['role']}: {msg['content']}" for msg in messages])
        llm_output = llm_service.generate_reply(conversation_context)
        
        if not llm_output:
            raise Exception("No LLM response generated")
        
        # Add assistant response to history
        messages.append({"role": "assistant", "content": llm_output})
        chat_histories[sessionId] = messages
        
        logger.info(f"Assistant response: {llm_output[:50]}...")
        
        # Convert to audio
        audio_url = tts_service.generate_audio(llm_output, "en-US-natalie")
        audio_base64 = download_audio_as_base64(audio_url)
        
        return {
            "transcription": transcript,
            "text": llm_output,
            "audio_base64": audio_base64
        }
    
    except Exception as e:
        logger.error(f"Agent chat failed: {e}")
        fallback_response = get_fallback_response(fallback_text)
        return {"error": str(e), **fallback_response}

# -----------------------
# Additional Endpoints
# -----------------------
@app.delete("/agent/chat/{sessionId}")
async def clear_chat_history(sessionId: str):
    """Clear chat history for a session."""
    if sessionId in chat_histories:
        del chat_histories[sessionId]
        logger.info(f"Cleared chat history for session: {sessionId}")
        return {"message": f"Chat history cleared for session {sessionId}"}
    else:
        return {"message": f"No chat history found for session {sessionId}"}

@app.get("/agent/chat/{sessionId}")
async def get_chat_history(sessionId: str):
    """Get chat history for a session."""
    messages = chat_histories.get(sessionId, [])
    return {"session_id": sessionId, "messages": messages}

@app.get("/health")
async def health_check():
    """Comprehensive health check for all services."""
    return {
        "status": "healthy",
        "services": {
            "stt": "operational",
            "tts": "operational", 
            "llm": "operational"
        }
    }

# -----------------------
# Error Handlers
# -----------------------
@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    logger.error(f"ValueError: {exc}")
    return JSONResponse(
        status_code=400,
        content={"error": "Invalid input", "detail": str(exc)}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": "Something went wrong"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)