import os
os.environ['HF_HUB_DISABLE_SYMLINKS_WARNING'] = '1'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # Suppress TensorFlow warnings
import sys
from pathlib import Path
from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv


load_dotenv()

app = FastAPI(title="Mood Music Recommender")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
templates = Jinja2Templates(directory=str(PROJECT_ROOT / "frontend"))
app.mount("/static", StaticFiles(directory=str(PROJECT_ROOT / "frontend" / "assets")), name="static")

from backend.app.services.spotify_service import SpotifyService
from backend.app.services.emotion_service import EmotionService
from backend.app.models.sentiment_analysis import SentimentAnalyzer
from backend.app.services.spotify_service import SpotifyService
from backend.app.utils.config import settings


# Initialize services
spotify_service = SpotifyService(
    client_id=os.getenv("SPOTIFY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
    redirect_uri=os.getenv("SPOTIFY_REDIRECT_URI")
)

emotion_service = EmotionService()
sentiment_analyzer = SentimentAnalyzer()

class EmotionInput(BaseModel):
    text: Optional[str] = None
    history: Optional[list] = None

class LanguagePreference(BaseModel):
    languages: list[str]

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/recommendations")
async def get_recommendations(emotion: str):
    try:
        spotify = SpotifyService()
        recommendations = spotify.get_recommendations(emotion)
        if not recommendations:
            raise HTTPException(status_code=404, detail="No recommendations found")
        return JSONResponse(content={"tracks": recommendations})
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

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
        spotify = SpotifyService()
        return {"auth_url": spotify.get_auth_url()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/spotify-callback")
async def spotify_callback(code: str):
    try:
        token = spotify_service.get_access_token(code)
        return {"status": "success", "access_token": token}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/user-history")
async def get_user_history(token: str):
    try:
        history = spotify_service.get_user_listening_history(token)
        return {"status": "success", "history": history}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)