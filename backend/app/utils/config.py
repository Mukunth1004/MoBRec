import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings:
    # Spotify API credentials
    SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
    SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
    SPOTIFY_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI", "http://localhost:8000/spotify-callback")
    
    # Model paths - these should be created when you train the models
    MODELS_DIR = BASE_DIR / "models"
    
    # Text emotion model
    TEXT_MODEL_PATH = MODELS_DIR / "text_emotion_model.joblib"
    
    # Listening history model
    HISTORY_MODEL_PATH = MODELS_DIR / "history_emotion_model.joblib"
    
    # Text vectorizer
    VECTORIZER_PATH = MODELS_DIR / "tfidf_vectorizer.joblib"
    
    # Create models directory if it doesn't exist
    if not MODELS_DIR.exists():
        MODELS_DIR.mkdir()

settings = Settings()