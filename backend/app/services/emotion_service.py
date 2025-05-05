from typing import List, Dict, Optional
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import SVC
from joblib import load
import os
from backend.app.models.sentiment_analysis import SentimentAnalyzer

class EmotionService:
    def __init__(self):
        # Initialize models
        self.text_model = self._load_text_model()
        self.history_model = self._load_history_model()
        self.vectorizer = self._load_vectorizer()
        self.sentiment_analyzer = SentimentAnalyzer()
        
        # Emotion labels
        self.emotions = ["happy", "sad", "angry", "calm", "energetic", "romantic"]
        
        # Audio features mapping to emotions
        self.feature_weights = {
            'danceability': {'happy': 0.8, 'sad': 0.2, 'angry': 0.5, 'calm': 0.3, 'energetic': 0.9, 'romantic': 0.6},
            'energy': {'happy': 0.7, 'sad': 0.3, 'angry': 0.9, 'calm': 0.2, 'energetic': 0.95, 'romantic': 0.5},
            'valence': {'happy': 0.9, 'sad': 0.1, 'angry': 0.4, 'calm': 0.6, 'energetic': 0.7, 'romantic': 0.8},
            'tempo': {'happy': 120, 'sad': 70, 'angry': 140, 'calm': 80, 'energetic': 130, 'romantic': 100}
        }

    def _load_text_model(self):
        # In a real app, this would load a pre-trained model
        # For demo, we'll use a simple model
        return None

    def _load_history_model(self):
        # In a real app, this would load a pre-trained model
        # For demo, we'll use a simple model
        return None

    def _load_vectorizer(self):
        # In a real app, this would load a pre-trained vectorizer
        # For demo, we'll use a simple vectorizer
        return None

    def detect_emotion_from_text(self, text: str) -> str:
        # First try sentiment analysis
        sentiment = self.sentiment_analyzer.analyze(text)
        
        # Map sentiment to emotion
        sentiment_mapping = {
            "POSITIVE": "happy",
            "NEGATIVE": "sad",
            "NEUTRAL": "calm"
        }
        
        base_emotion = sentiment_mapping.get(sentiment, "happy")
        
        # Enhance with keyword analysis
        keywords = {
            "happy": ["happy", "joy", "excited", "great", "awesome"],
            "sad": ["sad", "depressed", "lonely", "miss", "hurt"],
            "angry": ["angry", "mad", "hate", "annoyed", "frustrated"],
            "calm": ["calm", "peace", "relax", "chill", "quiet"],
            "energetic": ["energy", "pump", "workout", "party", "dance"],
            "romantic": ["love", "romantic", "heart", "kiss", "together"]
        }
        
        text_lower = text.lower()
        emotion_scores = {e: 0 for e in self.emotions}
        emotion_scores[base_emotion] += 1
        
        for emotion, words in keywords.items():
            for word in words:
                if word in text_lower:
                    emotion_scores[emotion] += 1
        
        # Get emotion with highest score
        detected_emotion = max(emotion_scores.items(), key=lambda x: x[1])[0]
        return detected_emotion

    def predict_emotion_from_history(self, history: List[Dict]) -> str:
        if not history:
            return "happy"  # default emotion
            
        # Calculate average audio features
        avg_features = {
            'danceability': np.mean([t.get('danceability', 0.5) for t in history]),
            'energy': np.mean([t.get('energy', 0.5) for t in history]),
            'valence': np.mean([t.get('valence', 0.5) for t in history]),
            'tempo': np.mean([t.get('tempo', 100) for t in history])
        }
        
        # Calculate similarity to each emotion's ideal features
        emotion_scores = {}
        for emotion in self.emotions:
            score = 0
            for feature, weights in self.feature_weights.items():
                if feature == 'tempo':
                    ideal_value = weights[emotion]
                    actual_value = avg_features[feature]
                    score += 1 - (abs(ideal_value - actual_value) / 200)  # normalize tempo difference
                else:
                    ideal_weight = weights[emotion]
                    actual_weight = avg_features[feature]
                    score += 1 - abs(ideal_weight - actual_weight)
            emotion_scores[emotion] = score
        
        # Get emotion with highest score
        predicted_emotion = max(emotion_scores.items(), key=lambda x: x[1])[0]
        return predicted_emotion