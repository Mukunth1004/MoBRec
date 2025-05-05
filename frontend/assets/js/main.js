document.addEventListener('DOMContentLoaded', function() {
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
        card.addEventListener('click', function() {
            const mood = this.getAttribute('data-mood');
            getRecommendations(mood);
        });
    });
    
    detectMoodBtn.addEventListener('click', function() {
        const text = moodText.value.trim();
        if (text) {
            detectEmotionFromText(text);
        } else {
            showAlert('Please describe your mood first');
        }
    });
    
    useHistoryBtn.addEventListener('click', function() {
        if (spotifyAccessToken) {
            predictEmotionFromHistory();
        } else {
            showAlert('Please connect your Spotify account first');
        }
    });
    
    spotifyAuthBtn.addEventListener('click', function() {
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
    
    // Double tap and triple tap detection for player controls
    setupGestureControls();

    // Functions
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

    function disconnectSpotify() {
        localStorage.removeItem('spotify_access_token');
        spotifyAccessToken = null;
        updateAuthUI();
        showAlert('Disconnected from Spotify', 'success');
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
            
            trackCard.addEventListener('click', function() {
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
        // Stop current playback
        audio.pause();
        clearInterval(progressInterval);
        
        // Update current track
        currentTrack = track;
        
        // Update player UI
        playerAlbumArt.src = track.image || 'https://via.placeholder.com/56';
        playerTrackName.textContent = track.name;
        playerTrackArtist.textContent = track.artists.join(', ');
        
        // Set audio source
        if (track.preview_url) {
            audio.src = track.preview_url;
            timeEnd.textContent = '0:30'; // Preview is usually 30 seconds
            playBtn.disabled = false;
        } else {
            audio.src = '';
            timeEnd.textContent = '0:00';
            playBtn.disabled = true;
        }
        
        // Show player
        player.style.display = 'flex';
        
        // Play if preview available
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
        if (isPlaying) {
            playBtn.innerHTML = '<i class="fas fa-pause"></i>';
        } else {
            playBtn.innerHTML = '<i class="fas fa-play"></i>';
        }
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
            
            // Update time display
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
        
        document.addEventListener('click', function(e) {
            tapCount++;
            
            if (tapCount === 1) {
                tapTimer = setTimeout(() => {
                    tapCount = 0;
                }, 300);
            } else if (tapCount === 2) {
                clearTimeout(tapTimer);
                tapCount = 0;
                
                // Double tap - skip 5 seconds
                if (currentTrack && currentTrack.preview_url) {
                    if (e.clientX < window.innerWidth / 2) {
                        // Left side - skip backward
                        audio.currentTime = Math.max(0, audio.currentTime - 5);
                    } else {
                        // Right side - skip forward
                        audio.currentTime = Math.min(audio.duration, audio.currentTime + 5);
                    }
                    updateProgressBar();
                }
            } else if (tapCount === 3) {
                clearTimeout(tapTimer);
                tapCount = 0;
                
                // Triple tap - play most replayed part (15-25s)
                if (currentTrack && currentTrack.preview_url) {
                    audio.currentTime = 15;
                    if (!isPlaying) {
                        audio.play();
                        isPlaying = true;
                        updatePlayButton();
                    }
                    
                    // After 10 seconds, return to start
                    setTimeout(() => {
                        audio.currentTime = 0;
                        updateProgressBar();
                    }, 10000);
                }
            }
        });
    }

    function showLoading(show) {
        const loader = document.getElementById('loading-overlay') || createLoader();
        loader.style.display = show ? 'flex' : 'none';
    }

    function createLoader() {
        const loader = document.createElement('div');
        loader.id = 'loading-overlay';
        loader.innerHTML = '<div class="loader"></div>';
        loader.style.display = 'none';
        document.body.appendChild(loader);
        return loader;
    }

    function showAlert(message, type = 'error') {
        const alert = document.createElement('div');
        alert.className = `alert ${type}`;
        alert.textContent = message;
        document.body.appendChild(alert);
        
        setTimeout(() => {
            alert.classList.add('show');
        }, 10);
        
        setTimeout(() => {
            alert.classList.remove('show');
            setTimeout(() => {
                document.body.removeChild(alert);
            }, 300);
        }, 3000);
    }

    function handleResponse(response) {
        if (!response.ok) {
            return response.json().then(err => {
                throw new Error(err.detail || 'Request failed');
            });
        }
        return response.json();
    }
});