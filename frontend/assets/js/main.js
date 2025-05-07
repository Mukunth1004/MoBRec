document.addEventListener('DOMContentLoaded', function () {
    // DOM Elements
    const moodCards = document.querySelectorAll('.mood-card');
    const detectMoodBtn = document.getElementById('detect-mood-btn');
    const moodText = document.getElementById('mood-text');
    const useHistoryBtn = document.getElementById('use-history-btn');
    const spotifyAuthBtn = document.getElementById('spotify-auth-btn');
    const recommendationsSection = document.getElementById('recommendations-section');
    const recommendationsGrid = document.getElementById('recommendations-grid');
    const player = document.getElementById('player');
    const playerAlbumArt = document.getElementById('player-album-art').querySelector('img');
    const playerTrackName = document.getElementById('player-track-name');
    const playerTrackArtist = document.getElementById('player-track-artist');
    const playBtn = document.getElementById('play-btn');
    const progressBar = document.getElementById('progress-bar');
    const progress = document.getElementById('progress');
    const timeStart = document.getElementById('time-start');
    const timeEnd = document.getElementById('time-end');
    const volumeSlider = document.getElementById('volume-slider');

    // Audio element for preview playback
    const audio = new Audio();
    let currentTrack = null;
    let isPlaying = false;
    let progressInterval = null;

    // Spotify OAuth
    let spotifyAccessToken = localStorage.getItem('spotify_access_token');

    // Check for Spotify callback on page load
    checkForSpotifyCallback();
    updateAuthUI();

    // Event Listeners
    moodCards.forEach(card => {
        card.addEventListener('click', function () {
            const mood = this.getAttribute('data-mood');
            getRecommendations(mood);
        });
    });

    detectMoodBtn.addEventListener('click', function () {
        const text = moodText.value.trim();
        if (text) {
            detectEmotionFromText(text);
        } else {
            showAlert('Please describe your mood first');
        }
    });

    useHistoryBtn.addEventListener('click', function () {
        if (spotifyAccessToken) {
            predictEmotionFromHistory();
        } else {
            showAlert('Please connect your Spotify account first');
        }
    });

    spotifyAuthBtn.addEventListener('click', function () {
        if (spotifyAccessToken) {
            disconnectSpotify();
        } else {
            initiateSpotifyAuth();
        }
    });

    playBtn.addEventListener('click', togglePlayback);
    progressBar.addEventListener('click', seekPlayback);
    volumeSlider.addEventListener('input', updateVolume);
    audio.addEventListener('timeupdate', updateProgressBar);
    audio.addEventListener('ended', handlePlaybackEnded);

    setupGestureControls();

    function checkForSpotifyCallback() {
        const urlParams = new URLSearchParams(window.location.search);
        const code = urlParams.get('code');
        const error = urlParams.get('error');

        if (error) {
            showAlert(`Spotify connection failed: ${error}`);
            window.history.replaceState({}, document.title, window.location.pathname);
            return;
        }

        if (code && !spotifyAccessToken) {
            fetch(`/spotify-callback?code=${code}`)
                .then(handleResponse)
                .then(data => {
                    if (data.access_token) {
                        spotifyAccessToken = data.access_token;
                        localStorage.setItem('spotify_access_token', spotifyAccessToken);
                        window.history.replaceState({}, document.title, window.location.pathname);
                        updateAuthUI();
                        showAlert('Successfully connected to Spotify!', 'success');
                    }
                })
                .catch(error => {
                    console.error('Spotify callback error:', error);
                    showAlert('Failed to connect with Spotify');
                });
        }
    }

    function updateAuthUI() {
        if (spotifyAccessToken) {
            spotifyAuthBtn.innerHTML = '<i class="fab fa-spotify"></i> Disconnect Spotify';
            spotifyAuthBtn.classList.add('connected');
            useHistoryBtn.style.display = 'flex';
        } else {
            spotifyAuthBtn.innerHTML = '<i class="fab fa-spotify"></i> Connect Spotify';
            spotifyAuthBtn.classList.remove('connected');
            useHistoryBtn.style.display = 'none';
        }
    }

    function initiateSpotifyAuth() {
        fetch('/spotify-auth')
            .then(handleResponse)
            .then(data => {
                window.location.href = data.auth_url;
            })
            .catch(error => {
                console.error('Spotify auth error:', error);
                showAlert('Failed to initiate Spotify connection');
            });
    }

    function detectEmotionFromText(text) {
        showLoading(true);
        fetch('/detect-emotion', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ text: text })
        })
            .then(handleResponse)
            .then(data => {
                if (data.emotion) {
                    getRecommendations(data.emotion);
                } else {
                    showAlert('Could not detect emotion from text');
                }
            })
            .catch(error => {
                console.error('Emotion detection error:', error);
                showAlert('Failed to detect emotion');
            })
            .finally(() => showLoading(false));
    }

    function predictEmotionFromHistory() {
        showLoading(true);
        fetch('/user-history', {
            headers: {
                'Authorization': `Bearer ${spotifyAccessToken}`
            }
        })
            .then(handleResponse)
            .then(data => {
                if (data.history) {
                    return fetch('/detect-emotion', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ history: data.history })
                    });
                }
                throw new Error('No history data received');
            })
            .then(handleResponse)
            .then(data => {
                if (data.emotion) {
                    getRecommendations(data.emotion);
                } else {
                    showAlert('Could not predict emotion from history');
                }
            })
            .catch(error => {
                console.error('History prediction error:', error);
                showAlert('Failed to predict emotion from history');
            })
            .finally(() => showLoading(false));
    }

    async function getRecommendations(emotion) {
        showLoading(true);
        try {
            const response = await fetch(`/recommendations?emotion=${emotion}`);
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Failed to get recommendations');
            }
            const data = await response.json();
            displayRecommendations(data.tracks);
        } catch (error) {
            console.error('Recommendation error:', error);
            showAlert(error.message || 'Failed to get recommendations');
        } finally {
            showLoading(false);
        }
    }

    function displayRecommendations(tracks) {
        recommendationsGrid.innerHTML = '';

        tracks.forEach(track => {
            const trackCard = document.createElement('div');
            trackCard.className = 'track-card';
            trackCard.innerHTML = `
                <img src="${track.image || 'https://via.placeholder.com/150'}" alt="${track.name}">
                <h4>${track.name}</h4>
                <p>${track.artists.join(', ')}</p>
                ${track.preview_url ? '<div class="play-icon"><i class="fas fa-play"></i></div>' : ''}
            `;

            trackCard.addEventListener('click', function () {
                playTrack(track);
            });

            recommendationsGrid.appendChild(trackCard);
        });

        recommendationsSection.style.display = 'block';
        window.scrollTo({
            top: recommendationsSection.offsetTop,
            behavior: 'smooth'
        });
    }

    function playTrack(track) {
        audio.pause();
        clearInterval(progressInterval);

        currentTrack = track;
        playerAlbumArt.src = track.image || 'https://via.placeholder.com/56';
        playerTrackName.textContent = track.name;
        playerTrackArtist.textContent = track.artists.join(', ');

        if (track.preview_url) {
            audio.src = track.preview_url;
            timeEnd.textContent = '0:30';
            playBtn.disabled = false;
        } else {
            audio.src = '';
            timeEnd.textContent = '0:00';
            playBtn.disabled = true;
        }

        player.style.display = 'flex';

        if (track.preview_url) {
            audio.play()
                .then(() => {
                    isPlaying = true;
                    updatePlayButton();
                })
                .catch(error => {
                    console.error('Playback error:', error);
                    isPlaying = false;
                    updatePlayButton();
                });
        }
    }

    function togglePlayback() {
        if (!currentTrack || !currentTrack.preview_url) return;

        if (isPlaying) {
            audio.pause();
        } else {
            audio.play();
        }

        isPlaying = !isPlaying;
        updatePlayButton();
    }

    function updatePlayButton() {
        playBtn.innerHTML = isPlaying ? '<i class="fas fa-pause"></i>' : '<i class="fas fa-play"></i>';
    }

    function seekPlayback(e) {
        if (!currentTrack || !currentTrack.preview_url) return;

        const percent = e.offsetX / this.offsetWidth;
        audio.currentTime = percent * audio.duration;
        updateProgressBar();
    }

    function updateProgressBar() {
        if (audio.duration) {
            const percent = (audio.currentTime / audio.duration) * 100;
            progress.style.width = `${percent}%`;

            const currentMinutes = Math.floor(audio.currentTime / 60);
            const currentSeconds = Math.floor(audio.currentTime % 60);
            timeStart.textContent = `${currentMinutes}:${currentSeconds < 10 ? '0' : ''}${currentSeconds}`;
        }
    }

    function handlePlaybackEnded() {
        isPlaying = false;
        updatePlayButton();
    }

    function updateVolume() {
        audio.volume = this.value / 100;
    }

    function setupGestureControls() {
        let tapCount = 0;
        let tapTimer = null;

        document.addEventListener('click', function (e) {
            tapCount++;

            if (tapCount === 1) {
                tapTimer = setTimeout(() => {
                    tapCount = 0;
                }, 300);
            } else if (tapCount === 2) {
                clearTimeout(tapTimer);
                togglePlayback();
                tapCount = 0;
            }
        });
    }

    function showAlert(message, type = 'error') {
        const alert = document.createElement('div');
        alert.classList.add('alert', type);
        alert.textContent = message;

        document.body.appendChild(alert);
        setTimeout(() => alert.remove(), 3000);
    }

    function showLoading(isLoading) {
        if (isLoading) {
            document.body.classList.add('loading');
        } else {
            document.body.classList.remove('loading');
        }
    }

    function handleResponse(response) {
        if (!response.ok) {
            return response.json().then(error => Promise.reject(error));
        }
        return response.json();
    }
});
