import base64
import requests
import random
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import os
from dotenv import load_dotenv

load_dotenv()

class SpotifyService:
    def __init__(self, client_id: str = None, client_secret: str = None, redirect_uri: str = None):
        self.client_id = client_id or os.getenv("SPOTIFY_CLIENT_ID")
        self.client_secret = client_secret or os.getenv("SPOTIFY_CLIENT_SECRET")
        self.redirect_uri = redirect_uri or os.getenv("SPOTIFY_REDIRECT_URI")
        self.base_url = "https://api.spotify.com/v1"
        self.token_url = "https://accounts.spotify.com/api/token"
        self.access_token = None
        self.token_expires = None
        self.scopes = "user-read-recently-played user-top-read playlist-read-private user-library-read"
        
        # Updated mood mapping with valid parameters
        self.mood_mapping = {
            "happy": {
                "seed_artists": "4NHQUGzhtTLFvgF5SZesLK",  # Clean Bandit
                "seed_tracks": "0VjIjW4GlUZAMYd2vXMi3b",  # Happy Now - Kygo
                "min_energy": 0.7,
                "min_valence": 0.7,
                "min_popularity": 50
            },
            "sad": {
                "seed_artists": "1dfeR4HaWDbWqFHLkxsg1d",  # Queen
                "seed_tracks": "6Uj1ctrBOjOas8xZXGqKk4",  # Someone Like You - Adele
                "max_energy": 0.4,
                "max_valence": 0.4,
                "min_popularity": 50
            }
        }
        
        # Updated valid genres
        self.valid_genres = [
            "pop", "rock", "hip-hop", "electronic", "indie",
            "jazz", "classical", "country", "r-n-b", "latin"
        ]
    def _get_auth_header(self):
        """Get authorization header with valid access token"""
        if not self.access_token or datetime.now() > self.token_expires:
            self._refresh_access_token()
        return {"Authorization": f"Bearer {self.access_token}"}

    
    def _refresh_access_token(self):
        """Refresh the access token using client credentials"""
        auth_string = f"{self.client_id}:{self.client_secret}"
        auth_bytes = auth_string.encode("utf-8")
        auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

        headers = {
            "Authorization": f"Basic {auth_base64}",
            "Content-Type": "application/x-www-form-urlencoded"
        }

        data = {"grant_type": "client_credentials"}
        
        response = requests.post(self.token_url, headers=headers, data=data)
        response.raise_for_status()
        
        token_data = response.json()
        self.access_token = token_data["access_token"]
        self.token_expires = datetime.now() + timedelta(seconds=token_data["expires_in"] - 60)


    def get_auth_url(self) -> str:
        params = {
            "client_id": self.client_id,
            "response_type": "code",
            "redirect_uri": self.redirect_uri,
            "scope": self.scopes,
            "show_dialog": "true"
        }
        return f"https://accounts.spotify.com/authorize?{urlencode(params)}"

    def get_access_token(self, code: str) -> Dict:
        """Exchange authorization code for access token"""
        auth_string = f"{self.client_id}:{self.client_secret}"
        auth_bytes = auth_string.encode("utf-8")
        auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

        headers = {
            "Authorization": f"Basic {auth_base64}",
            "Content-Type": "application/x-www-form-urlencoded"
        }

        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.redirect_uri
        }

        response = requests.post(self.token_url, headers=headers, data=data)
        response.raise_for_status()
        return response.json()

    def get_user_listening_history(self, token: str, limit: int = 50) -> List[Dict]:
        """Get user's recently played and top tracks"""
        headers = {"Authorization": f"Bearer {token}"}
        
        # Get recently played tracks
        recently_played_url = f"{self.base_url}/me/player/recently-played?limit={limit}"
        response = requests.get(recently_played_url, headers=headers)
        response.raise_for_status()
        recently_played = response.json().get("items", [])
        
        # Get top tracks
        top_tracks_url = f"{self.base_url}/me/top/tracks?limit={limit//2}"
        response = requests.get(top_tracks_url, headers=headers)
        top_tracks = response.json().get("items", []) if response.status_code == 200 else []
        
        # Combine and process tracks
        all_tracks = recently_played + top_tracks
        processed_tracks = []
        
        for item in all_tracks:
            track = item.get("track", item)
            processed_tracks.append({
                "id": track["id"],
                "name": track["name"],
                "artists": [artist["name"] for artist in track["artists"]],
                "uri": track["uri"],
                "popularity": track.get("popularity", 0)
            })
        
        return processed_tracks

    
    def get_recommendations(self, mood: str, limit: int = 20) -> List[Dict]:
        if not self.access_token:
            self._refresh_access_token()

        mood = mood.lower()
        if mood not in self.mood_mapping:
            mood = "happy"  # Default to happy

        params = {
            "limit": limit,
            "seed_genres": ",".join(random.sample(self.valid_genres, 2)),
            "seed_artists": self.mood_mapping[mood]["seed_artists"],
            "seed_tracks": self.mood_mapping[mood]["seed_tracks"],
            "min_popularity": 50
        }
        
        # Add mood-specific params
        if "min_energy" in self.mood_mapping[mood]:
            params["min_energy"] = self.mood_mapping[mood]["min_energy"]
        if "max_energy" in self.mood_mapping[mood]:
            params["max_energy"] = self.mood_mapping[mood]["max_energy"]
        if "min_valence" in self.mood_mapping[mood]:
            params["min_valence"] = self.mood_mapping[mood]["min_valence"]
        if "max_valence" in self.mood_mapping[mood]:
            params["max_valence"] = self.mood_mapping[mood]["max_valence"]

        try:
            response = requests.get(
                f"{self.base_url}/recommendations",
                headers=self._get_auth_header(),
                params=params
            )
            response.raise_for_status()
            return response.json()["tracks"]
        except requests.exceptions.HTTPError as e:
            print(f"Spotify API Error: {e.response.text}")
            return []
        except Exception as e:
            print(f"Error getting recommendations: {e}")
            return []

    def _get_trending_tracks(self, languages: List[str]) -> List[str]:
        """Get trending track IDs for seed tracks"""
        # In production, fetch from Spotify's trending playlists
        trending_tracks = {
            "en": ["4cOdK2wGLETKBW3PvgPWqT", "7GhIk7Il098yCjg4BQjzvb", "3ee8Jmje8o58CHK66QrVC2"],
            "hi": ["0ceBi8YHQ0wQ0XSWVVVSmX", "4IKZ1JZkw9N1tH6omx6kX7", "5SZ6KG64m5ucGe9jV9N1BG"],
            "ta": ["6T7G08BiBTWJhbYI4dC6qT", "3g9hB0WRNHj3Hk1s3LZ4Jk", "5SZ6KG64m5ucGe9jV9N1BG"],
            "te": ["4cOdK2wGLETKBW3PvgPWqT", "7GhIk7Il098yCjg4BQjzvb", "3ee8Jmje8o58CHK66QrVC2"],
            "ml": ["6T7G08BiBTWJhbYI4dC6qT", "3g9hB0WRNHj3Hk1s3LZ4Jk", "5SZ6KG64m5ucGe9jV9N1BG"]
        }
        
        seeds = []
        for lang in languages:
            seeds.extend(trending_tracks.get(lang, []))
        
        return seeds

    def _get_evergreen_hit(self, lang: str, market: str) -> Optional[Dict]:
        """Get an evergreen hit for the specified language"""
        evergreen_tracks = {
            "en": "7ouMYWpwJ422jRcDASZB7P",  # Shape of You
            "hi": "0ceBi8YHQ0wQ0XSWVVVSmX",  # Tujhe Kitna Chahne Lage
            "ta": "6T7G08BiBTWJhbYI4dC6qT",  # Why This Kolaveri Di
            "te": "4cOdK2wGLETKBW3PvgPWqT",  # Butta Bomma
            "ml": "5SZ6KG64m5ucGe9jV9N1BG"   # Malare
        }
        
        track_id = evergreen_tracks.get(lang)
        if not track_id:
            return None
        
        url = f"{self.base_url}/tracks/{track_id}"
        params = {"market": market}
        
        try:
            response = requests.get(url, headers=self._get_auth_header(), params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error getting evergreen track for {lang}: {e}")
            return None