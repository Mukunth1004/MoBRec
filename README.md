# Mood-Based Music Recommendation System

A web application that recommends music based on user mood and tracks the user's mood history. The system uses natural language processing (NLP) to detect emotions from text and leverages the Spotify API for personalized recommendations. 

---

## Features

- **Mood Detection**: Users can describe their mood, and the system will recommend music based on the detected emotion.
- **Spotify Integration**: Connect your Spotify account to access music history for personalized recommendations.
- **Track Preview**: Listen to track previews directly from the app.
- **Gesture Controls**: Use simple gestures like double-tap to toggle music playback.

---

## Technologies Used

- **Frontend**: HTML, CSS, JavaScript
- **Backend**: Node.js, Express.js
- **Spotify API**: Used for fetching personalized music recommendations and user history
- **Emotion Detection**: NLP models for emotion detection based on user input
- **OAuth**: For connecting Spotify to the app
- **Audio Preview**: HTML5 `<audio>` for track previews

---

## Setup Instructions

### Prerequisites

1. Clone the repository:
    ```bash
    git clone https://github.com/your-username/mood-music-recommendation.git
    cd mood-music-recommendation
    ```

2. Install dependencies:
    ```bash
    npm install
    ```

3. Set up environment variables:
    - Create a `.env` file in the root directory and add your Spotify credentials (client ID, client secret, etc.).

4. Run the application:
    ```bash
    npm start
    ```

5. Visit `http://localhost:3000` in your browser to view the app.

---

## How to Use

1. **Connect Spotify**:
   - Click the "Connect Spotify" button to authorize your Spotify account.
   
2. **Detect Mood**:
   - Type your mood in the text box and click "Detect Mood" to receive music recommendations based on your emotion.

3. **Use Mood History**:
   - Click "Use History" to predict your mood from your Spotify listening history and receive personalized recommendations.

4. **Play Track**:
   - Click on a recommended track to start listening to a preview.

---

## Screenshots

Here is a preview of the app:

[Screenshot]("D:\Projects\MoBRec\screenshot\Screenshot 2025-05-06 111950.png")  <!-- Replace with the actual image path -->
[Screenshot]("D:\Projects\MoBRec\screenshot\Screenshot 2025-05-07 115628.png")
---

## Contributing

Feel free to fork the repository and submit pull requests! Here are some ways you can help improve the project:

- Adding new features
- Fixing bugs
- Improving the UI/UX

---

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

---

## Acknowledgements

- **Spotify API** for music recommendations and user data
- **NLP libraries** used for emotion detection
