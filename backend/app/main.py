import os
os.environ['HF_HUB_DISABLE_SYMLINKS_WARNING'] = '1'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # Suppress TensorFlow warnings
import sys
from pathlib import Path
from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict
from dotenv import load_dotenv
import logging as logger
import uvicorn

# Set up paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

load_dotenv()

# Initialize FastAPI
app = FastAPI(title="Mood Music Recommender")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://b390-2401-4900-4df9-d2da-782a-ec44-aee4-8c34.ngrok-free.app",  # Allow ngrok frontend URL
        "https://localhost:3000"  # Allow local frontend URL for development
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


# Set up templates and static files
templates = Jinja2Templates(directory=str(PROJECT_ROOT / "frontend"))
app.mount("/static", StaticFiles(directory=str(PROJECT_ROOT / "frontend" / "assets")), name="static")

# Import services after path setup
from backend.app.services.spotify_service import SpotifyService
from backend.app.services.emotion_service import EmotionService
from backend.app.models.sentiment_analysis import SentimentAnalyzer

spotify_service = SpotifyService()

# Initialize services with proper error handling
try:
    spotify_service = SpotifyService(
        client_id=os.getenv("SPOTIFY_CLIENT_ID"),
        client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
        redirect_uri=os.getenv("SPOTIFY_REDIRECT_URI")
    )
    emotion_service = EmotionService()
    sentiment_analyzer = SentimentAnalyzer()
except Exception as e:
    print(f"Failed to initialize services: {str(e)}")
    raise

# Models
class EmotionInput(BaseModel):
    text: Optional[str] = None
    history: Optional[list] = None

class LanguagePreference(BaseModel):
    languages: list[str]

# Routes
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/recommendations")
def get_recommendations(emotion: str):
    tracks = spotify_service.get_recommendations(emotion)
    if not tracks:
        raise HTTPException(status_code=400, detail="Could not fetch recommendations")
    return {"tracks": tracks}

@app.post("/detect-emotion")
async def detect_emotion(data: EmotionInput):
    try:
        if data.text:
            emotion = emotion_service.detect_emotion_from_text(data.text)
        elif data.history:
            emotion = emotion_service.predict_emotion_from_history(data.history)
        else:
            raise HTTPException(status_code=400, detail="Either text or history must be provided")
        
        return {"status": "success", "emotion": emotion}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/spotify-auth")
async def spotify_auth():
    try:
        auth_url = spotify_service.get_auth_url()
        return {"auth_url": auth_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/spotify-callback")
async def spotify_callback(code: str, state: Optional[str] = None):
    try:
        token_data = spotify_service.get_access_token(code)
        # Redirect to frontend with token in URL fragment
        access_token = token_data['access_token']
        frontend_url = f"https://b390-2401-4900-4df9-d2da-782a-ec44-aee4-8c34.ngrok-free.app/spotify-callback#access_token={access_token}&token_type={token_data['token_type']}&expires_in={token_data['expires_in']}"
        
        # Log the URL you're redirecting to
        print(f"Redirecting to: {frontend_url}")
        
        return RedirectResponse(url=frontend_url)
    except Exception as e:
        error_url = f"https://b390-2401-4900-4df9-d2da-782a-ec44-aee4-8c34.ngrok-free.app/spotify-callback?error={str(e)}"
        return RedirectResponse(url=error_url)


@app.get("/user-history")
async def get_user_history(token: str):
    try:
        history = spotify_service.get_user_listening_history(token)
        return {"status": "success", "history": history}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
    app,
    host="0.0.0.0",
    port=8000
)
