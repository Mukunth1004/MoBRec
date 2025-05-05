from pydantic import BaseModel
from typing import List, Optional

class Track(BaseModel):
    id: str
    name: str
    artists: List[str]
    uri: str
    popularity: int

class AudioFeatures(BaseModel):
    danceability: float
    energy: float
    valence: float
    tempo: float
    acousticness: Optional[float] = None
    instrumentalness: Optional[float] = None
    liveness: Optional[float] = None
    loudness: Optional[float] = None

class RecommendationRequest(BaseModel):
    emotion: str
    languages: List[str]
    limit: Optional[int] = 20

class SpotifyAuthResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    refresh_token: Optional[str] = None
    scope: Optional[str] = None

class UserHistoryResponse(BaseModel):
    tracks: List[Track]
    audio_features: Optional[List[AudioFeatures]] = None