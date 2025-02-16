// YouTube Player variables
let player;
let currentVideoId;
let playerBarVisible = false; // Added: variable to track player bar visibility

// Add liked songs storage
let likedSongs = new Set(JSON.parse(localStorage.getItem('likedSongs') || '[]'));

document.addEventListener("DOMContentLoaded", function() {
    initializeUI();
    setupEventListeners();
    loadYouTubeAPI();
});

function loadYouTubeAPI() {
    // Load YouTube IFrame API
    const tag = document.createElement('script');
    tag.src = "https://www.youtube.com/iframe_api";
    const firstScriptTag = document.getElementsByTagName('script')[0];
    firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);
}

// Called automatically by YouTube API
window.onYouTubeIframeAPIReady = function() {
    // Create a hidden player
    player = new YT.Player('youtube-player', {
        height: '0',
        width: '0',
        videoId: '',
        playerVars: {
            'playsinline': 1,
            'controls': 0,
            'disablekb': 1
        },
        events: {
            'onReady': onPlayerReady,
            'onStateChange': onPlayerStateChange,
            'onError': onPlayerError
        }
    });
}

function onPlayerReady(event) {
    console.log("YouTube player is ready");
}

function onPlayerStateChange(event) {
    switch(event.data) {
        case YT.PlayerState.PLAYING:
            updatePlayPauseButton(true);
            break;
        case YT.PlayerState.PAUSED:
        case YT.PlayerState.ENDED:
            updatePlayPauseButton(false);
            break;
    }
}

function onPlayerError(event) {
    console.error("Player error:", event.data);
    updatePlayPauseButton(false);
}

function initializeUI() {
    fetchTrendingSongs();
    fetchNewReleases();
    fetchYourMix();
    fetchFeaturedSongs();
    fetchHindiSongs();
    fetchPunjabiSongs();
    fetchEnglishSongs();
    fetchAlbums();
}

function updatePlayPauseButton(isPlaying) {
    const playIcon = document.querySelector('.play');
    const pauseIcon = document.querySelector('.pause');
    if (playIcon && pauseIcon) {
        if (isPlaying) {
            playIcon.classList.add('hidden');
            pauseIcon.classList.remove('hidden');
        } else {
            playIcon.classList.remove('hidden');
            pauseIcon.classList.add('hidden');
        }
    }
}

async function playSong(videoId, title, artist, thumbnail) {
    try {
        // Show player bar if hidden
        const playerBar = document.getElementById('now-playing-bar');
        if (playerBar && !playerBarVisible) {
            playerBar.classList.add('visible');
            playerBarVisible = true;
        }

        // Update current track info
        currentVideoId = videoId;
        document.getElementById('current-song-title').textContent = title;
        document.getElementById('current-song-artist').textContent = artist;
        document.getElementById('current-song-image').src = thumbnail;

        // Update like button state
        const likeBtn = document.querySelector('.like-btn');
        if (likeBtn) {
            likeBtn.classList.toggle('active', likedSongs.has(videoId));
        }

        if (player && player.loadVideoById) {
            if (videoId === currentVideoId && (!player.getPlayerState || player.getPlayerState() === YT.PlayerState.PLAYING)) {
                player.pauseVideo();
            } else {
                player.loadVideoById(videoId);
                player.playVideo();
            }
        } else {
            console.error("YouTube player not ready");
        }
    } catch (error) {
        console.error("Error playing song:", error);
    }
}

function togglePlay() {
    if (!player || !currentVideoId) return;

    try {
        const state = player.getPlayerState();
        if (state === YT.PlayerState.PLAYING) {
            player.pauseVideo();
        } else {
            player.playVideo();
        }
    } catch (error) {
        console.error("Error toggling play state:", error);
    }
}

async function fetchFeaturedSongs() {
    const featured = document.getElementById("featured-songs");
    if (!featured) return;

    try {
        const response = await fetch('/api/featured');
        if (!response.ok) throw new Error('Failed to fetch featured songs');

        const songs = await response.json();
        updateSongList(featured, songs, "No featured songs available");
    } catch (error) {
        console.error("Error fetching featured songs:", error);
        showError(featured, "Failed to load featured songs");
    }
}

async function fetchTrendingSongs() {
    const trending = document.getElementById("trending-songs");
    if (!trending) return;

    try {
        const response = await fetch('/api/trending');
        if (!response.ok) throw new Error('Failed to fetch trending songs');

        const songs = await response.json();
        updateSongList(trending, songs, "No trending songs available");
    } catch (error) {
        console.error("Error fetching trending songs:", error);
        showError(trending, "Failed to load trending songs");
    }
}

async function fetchNewReleases() {
    const newReleases = document.getElementById("new-releases");
    if (!newReleases) return;

    try {
        const response = await fetch('/api/new-releases');
        if (!response.ok) throw new Error('Failed to fetch new releases');

        const songs = await response.json();
        updateSongList(newReleases, songs, "No new releases available");
    } catch (error) {
        console.error("Error fetching new releases:", error);
        showError(newReleases, "Failed to load new releases");
    }
}

async function fetchYourMix() {
    const yourMix = document.getElementById("your-mix");
    if (!yourMix) return;

    try {
        const response = await fetch('/api/your-mix');
        if (!response.ok) throw new Error('Failed to fetch your mix');

        const songs = await response.json();
        updateSongList(yourMix, songs, "No personalized mix available");
    } catch (error) {
        console.error("Error fetching your mix:", error);
        showError(yourMix, "Failed to load your mix");
    }
}

function updateSongList(container, songs, emptyMessage) {
    if (!container) return;

    if (!songs || songs.length === 0) {
        container.innerHTML = `<div class="error">${emptyMessage}</div>`;
        return;
    }

    container.innerHTML = songs.map(song => createSongCard(song)).join('');
}

function showError(container, message) {
    if (container) {
        container.innerHTML = `<div class="error">${message}</div>`;
    }
}

function createSongCard(song) {
    const title = song.title ? song.title.replace(/'/g, '&#39;') : 'Unknown Title';
    const artist = song.artist ? song.artist.replace(/'/g, '&#39;') : 'Unknown Artist';
    const views = song.views ? parseInt(song.views).toLocaleString() : '0';
    const thumbnail = song.thumbnail || 'https://via.placeholder.com/150?text=No+Thumbnail';

    return `
        <div class="song-card" onclick="playSong('${song.videoId}', '${title}', '${artist}', '${thumbnail}')">
            <img src="${thumbnail}" alt="${title}" loading="lazy" onerror="this.src='https://via.placeholder.com/150?text=No+Thumbnail';">
            <p class="song-title">${title}</p>
            <p class="artist">${artist}</p>
            <p class="views">👁 ${views} views</p>
        </div>
    `;
}

function setupEventListeners() {
    // Search functionality
    const searchBar = document.getElementById('searchBar');
    if (searchBar) {
        let searchTimeout;
        searchBar.addEventListener('input', function(e) {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                if (e.target.value.trim()) {
                    searchSongs(e.target.value);
                }
            }, 500);  // Debounce search for 500ms
        });
    }

    // Player controls
    setupPlayerControls();

    // Add mobile menu toggle functionality
    const menuToggle = document.querySelector('.menu-toggle');
    const sidebar = document.querySelector('.sidebar');

    if (menuToggle && sidebar) {
        menuToggle.addEventListener('click', () => {
            sidebar.classList.toggle('active');
        });

        // Close sidebar when clicking outside
        document.addEventListener('click', (e) => {
            if (!sidebar.contains(e.target) && !menuToggle.contains(e.target)) {
                sidebar.classList.remove('active');
            }
        });
    }

    // Add profile button click handler
    const profileBtn = document.querySelector('.profile-btn');
    if (profileBtn) {
        profileBtn.addEventListener('click', () => {
            window.location.href = '/login';
        });
    }

    // Add settings button click handler
    const settingsBtn = document.querySelector('[data-settings-button]');
    if (settingsBtn) {
        settingsBtn.addEventListener('click', openSettings);
    }

    // Check user profile on load
    checkUserProfile();
}

function setupPlayerControls() {
    // Play/Pause button
    const playPauseBtn = document.querySelector('.play-pause');
    if (playPauseBtn) {
        playPauseBtn.addEventListener('click', togglePlay);
    }

    // Previous track button
    const prevBtn = document.querySelector('.previous');
    if (prevBtn) {
        prevBtn.addEventListener('click', previousTrack);
    }

    // Next track button
    const nextBtn = document.querySelector('.next');
    if (nextBtn) {
        nextBtn.addEventListener('click', nextTrack);
    }

    // Volume controls
    const volumeBar = document.querySelector('.volume-bar');
    if (volumeBar) {
        volumeBar.addEventListener('click', adjustVolume);
    }

    // Like button
    const likeBtn = document.querySelector('.like-btn');
    if (likeBtn) {
        likeBtn.addEventListener('click', toggleLike);
    }
}

let isPlaying = false;
let currentTrack = null;


function previousTrack() {
    console.log('Previous track');
    // Implement previous track functionality
}

function nextTrack() {
    console.log('Next track');
    // Implement next track functionality
}

function adjustVolume(e) {
    const volumeBar = e.currentTarget;
    const rect = volumeBar.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const percentage = (x / rect.width) * 100;

    const volumeProgress = volumeBar.querySelector('.volume-progress');
    if (volumeProgress) {
        volumeProgress.style.width = `${percentage}%`;
    }

    // Here you would typically set the actual volume
    console.log(`Volume set to: ${Math.round(percentage)}%`);
}

async function searchSongs(query) {
    const searchResults = document.getElementById('search-results');
    if (!searchResults) return;

    try {
        const response = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
        if (!response.ok) throw new Error('Search failed');

        const results = await response.json();
        updateSongList(searchResults, results, "No songs found matching your search");
    } catch (error) {
        console.error("Error searching songs:", error);
        showError(searchResults, "Failed to perform search");
    }
}

function getYouTubeThumbnail(videoId) {
    return `https://img.youtube.com/vi/${videoId}/hqdefault.jpg`;
}

// Update toggleLike to use backend API
async function toggleLike() {
    if (!currentVideoId) return;

    try {
        const endpoint = likedSongs.has(currentVideoId) ? 
            `/api/unlike-song/${currentVideoId}` : 
            `/api/like-song/${currentVideoId}`;

        const response = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });

        if (!response.ok) {
            if (response.status === 401) {
                window.location.href = '/login';
                return;
            }
            throw new Error('Failed to update like status');
        }

        const likeBtn = document.querySelector('.like-btn');
        if (likedSongs.has(currentVideoId)) {
            likedSongs.delete(currentVideoId);
            likeBtn.classList.remove('active');
        } else {
            likedSongs.add(currentVideoId);
            likeBtn.classList.add('active');
        }

        // Save to localStorage
        localStorage.setItem('likedSongs', JSON.stringify([...likedSongs]));

    } catch (error) {
        console.error("Error toggling like:", error);
    }
}

// Add user profile management
async function checkUserProfile() {
    try {
        const response = await fetch('/api/user-profile');
        const data = await response.json();
        updateProfileUI(data);
    } catch (error) {
        console.error("Error checking user profile:", error);
    }
}

function updateProfileUI(profileData) {
    const profileBtn = document.querySelector('.profile-btn');
    if (profileData.authenticated) {
        if (profileData.avatar) {
            profileBtn.innerHTML = `<img src="${profileData.avatar}" alt="${profileData.username}" class="profile-avatar">`;
        }
        profileBtn.title = profileData.username;
    } else {
        profileBtn.innerHTML = `
            <svg viewBox="0 0 24 24" class="icon">
                <path fill="currentColor" d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 3c1.66 0 3 1.34 3 3s-1.34 3-3 3-3-1.34-3-3 1.34-3 3-3zm0 14.2c-2.5 0-4.71-1.28-6-3.22.03-1.99 4-3.08 6-3.08 1.99 0 5.97 1.09 6 3.08-1.29 1.94-3.5 3.22-6 3.22z"/>
            </svg>
        `;
        profileBtn.title = "Login with Discord";
    }
}

// Add settings functionality
function openSettings() {
    const settingsPanel = document.getElementById('settings-panel');
    if (settingsPanel) {
        settingsPanel.classList.add('visible');
    }
}

function closeSettings() {
    const settingsPanel = document.getElementById('settings-panel');
    if (settingsPanel) {
        settingsPanel.classList.remove('visible');
    }
}

async function fetchHindiSongs() {
    const hindiSongs = document.getElementById("hindi-songs");
    if (!hindiSongs) return;

    try {
        const response = await fetch('/api/hindi');
        if (!response.ok) throw new Error('Failed to fetch Hindi songs');

        const songs = await response.json();
        updateSongList(hindiSongs, songs, "No Hindi songs available");
    } catch (error) {
        console.error("Error fetching Hindi songs:", error);
        showError(hindiSongs, "Failed to load Hindi songs");
    }
}

async function fetchPunjabiSongs() {
    const punjabiSongs = document.getElementById("punjabi-songs");
    if (!punjabiSongs) return;

    try {
        const response = await fetch('/api/punjabi');
        if (!response.ok) throw new Error('Failed to fetch Punjabi songs');

        const songs = await response.json();
        updateSongList(punjabiSongs, songs, "No Punjabi songs available");
    } catch (error) {
        console.error("Error fetching Punjabi songs:", error);
        showError(punjabiSongs, "Failed to load Punjabi songs");
    }
}

async function fetchEnglishSongs() {
    const englishSongs = document.getElementById("english-songs");
    if (!englishSongs) return;

    try {
        const response = await fetch('/api/english');
        if (!response.ok) throw new Error('Failed to fetch English songs');

        const songs = await response.json();
        updateSongList(englishSongs, songs, "No English songs available");
    } catch (error) {
        console.error("Error fetching English songs:", error);
        showError(englishSongs, "Failed to load English songs");
    }
}

async function fetchAlbums() {
    const albums = document.getElementById("albums");
    if (!albums) return;

    try {
        const response = await fetch('/api/albums');
        if (!response.ok) throw new Error('Failed to fetch albums');

        const songs = await response.json();
        updateSongList(albums, songs, "No albums available");
    } catch (error) {
        console.error("Error fetching albums:", error);
        showError(albums, "Failed to load albums");
    }
}