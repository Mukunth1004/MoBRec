import base64
import requests
import os
from datetime import datetime, timedelta
from urllib.parse import urlencode
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SpotifyService:
    def __init__(self, client_id=None, client_secret=None, redirect_uri=None):
        self.client_id = client_id or os.getenv("SPOTIFY_CLIENT_ID")
        self.client_secret = client_secret or os.getenv("SPOTIFY_CLIENT_SECRET")
        self.redirect_uri = redirect_uri or os.getenv("SPOTIFY_REDIRECT_URI")
        self.access_token = None
        self.token_expiration = datetime.utcnow()

        if not all([self.client_id, self.client_secret, self.redirect_uri]):
            raise ValueError("Missing Spotify credentials.")

    def _refresh_access_token(self):
        """Uses client credentials flow"""
        logger.info("Refreshing Spotify access token...")

        auth_header = base64.b64encode(f"{self.client_id}:{self.client_secret}".encode()).decode()
        headers = {
            "Authorization": f"Basic {auth_header}",
            "Content-Type": "application/x-www-form-urlencoded"
        }

        data = {
            "grant_type": "client_credentials"
        }

        response = requests.post("https://accounts.spotify.com/api/token", headers=headers, data=data)
        response.raise_for_status()
        token_info = response.json()

        self.access_token = token_info["access_token"]
        self.token_expiration = datetime.utcnow() + timedelta(seconds=token_info["expires_in"])
        logger.info("Spotify token refreshed.")

    def _ensure_token(self):
        if not self.access_token or datetime.utcnow() >= self.token_expiration:
            self._refresh_access_token()

    def get_auth_url(self):
        """Use for Authorization Code Flow (user access)"""
        params = {
            "client_id": self.client_id,
            "response_type": "code",
            "redirect_uri": self.redirect_uri,
            "scope": "user-read-recently-played user-top-read",
        }
        return f"https://accounts.spotify.com/authorize?{urlencode(params)}"

    def get_access_token(self, code):
        """Authorization Code Flow - exchange code for access token"""
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.redirect_uri,
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }

        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }

        response = requests.post("https://accounts.spotify.com/api/token", data=data, headers=headers)
        response.raise_for_status()
        return response.json()

    def get_valid_seed_genres(self):
        self._ensure_token()

        endpoint = "https://api.spotify.com/v1/recommendations/available-genre-seeds"
        headers = {
            "Authorization": f"Bearer {self.access_token}"
        }

        logger.info(f"Getting seed genres with token: {self.access_token}")
        response = requests.get(endpoint, headers=headers)
        response.raise_for_status()
        return response.json().get("genres", [])

    def get_recommendations(self, mood: str, language: str = None):
        """Returns predefined recommendations based on mood (happy, sad, etc.) and language"""
        predefined_recommendations = {
            "happy": [
                {"name": "Happy", "artists": ["Pharrell Williams"], "url": "https://spotify.com", "preview_url": "https://open.spotify.com/track/0h1ti3sC21H94a8sqAlpcj", "album_image": "https://i.scdn.co/image/ab67616d0000b2731e95a7226d90393c8ff3bc36"},
                {"name": "Can't Stop the Feeling!", "artists": ["Justin Timberlake"], "url": "https://spotify.com", "preview_url": "https://open.spotify.com/track/6J6R3ZuBYE8BhUcu57NE7u", "album_image": "https://i.scdn.co/image/ab67616d0000b27317cced61f45e912a8db0e06c"},
                {"name": "Shake It Off", "artists": ["Taylor Swift"], "url": "https://spotify.com", "preview_url": "https://open.spotify.com/track/6cD1rZd7gVORdpUyNs5Ics", "album_image": "https://i.scdn.co/image/ab67616d0000b2731b411e747456705f79f05651"}
            ],
            "sad": [
                {"name": "Someone Like You", "artists": ["Adele"], "url": "https://spotify.com", "preview_url": "https://open.spotify.com/track/7mH9W1QZbwzQktoc32Bh8V", "album_image": "https://i.scdn.co/image/ab67616d0000b273cc1638e2b5d85b616189af9b"},
                {"name": "The Night We Met", "artists": ["Lord Huron"], "url": "https://spotify.com", "preview_url": "https://open.spotify.com/track/4j6B8QjIHb6b27bS2ec9V0", "album_image": "https://i.scdn.co/image/ab67616d0000b273111b6f59b0f3b4d1182b871f"},
                {"name": "All I Want", "artists": ["Kodaline"], "url": "https://spotify.com", "preview_url": "https://open.spotify.com/track/39jmjc5oRJrFVeLR9lt7bY", "album_image": "https://i.scdn.co/image/ab67616d0000b27347ec233f7b7359a7647f87b1"}
            ]
        }

        if mood not in predefined_recommendations:
            raise Exception(f"Recommendations not available for mood: {mood}")

        # Filter by language if provided (for now, assuming `language` is a valid language filter)
        mood_recommendations = predefined_recommendations[mood]

        if language:
            # Apply language-based filter here (dummy logic for now)
            mood_recommendations = [track for track in mood_recommendations if language.lower() in track["name"].lower()]

        return mood_recommendations

    def get_user_listening_history(self, token: str):
        """Fetch user listening history using a user access token"""
        headers = {
            "Authorization": f"Bearer {token}"
        }

        response = requests.get("https://api.spotify.com/v1/me/player/recently-played", headers=headers)
        if response.status_code != 200:
            logger.error(f"Spotify user history error: {response.status_code} - {response.text}")
            raise Exception("Failed to fetch user listening history.")

        return response.json().get("items", [])

    def refresh_user_token(self, refresh_token):
        """Optional: Refresh user token using refresh_token (if needed for user login flow)"""
        data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }

        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }

        response = requests.post("https://accounts.spotify.com/api/token", data=data, headers=headers)
        response.raise_for_status()
        token_info = response.json()
        self.access_token = token_info["access_token"]
        self.token_expiration = datetime.utcnow() + timedelta(seconds=token_info["expires_in"])
        return token_info

# Example Usage:
if __name__ == "__main__":
    spotify_service = SpotifyService(client_id="your_client_id", client_secret="your_client_secret", redirect_uri="your_redirect_uri")

    try:
        mood = "happy"  # Change mood to "sad" for sad recommendations
        recommendations = spotify_service.get_recommendations(mood)
        for rec in recommendations:
            print(f"Track Name: {rec['name']}")
            print(f"Artists: {', '.join(rec['artists'])}")
            print(f"URL: {rec['url']}")
            print(f"Preview: {rec['preview_url']}")
            print(f"Album Image: {rec['album_image']}")
            print("-" * 40)
    except Exception as e:
        logger.error(f"Error: {e}")
