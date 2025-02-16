document.addEventListener("DOMContentLoaded", function() {
    initializeUI();
    setupEventListeners();
});

function initializeUI() {
    fetchTrendingSongs();
    fetchNewReleases();
    fetchYourMix();
    fetchFeaturedSongs();
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
}

let isPlaying = false;
let currentTrack = null;

function playSong(videoId, title, artist, thumbnail) {
    currentTrack = { videoId, title, artist, thumbnail };

    // Update player UI
    document.getElementById('current-song-title').textContent = title;
    document.getElementById('current-song-artist').textContent = artist;
    document.getElementById('current-song-image').src = thumbnail;

    // Reset play button state
    const playIcon = document.querySelector('.play');
    const pauseIcon = document.querySelector('.pause');
    if (playIcon && pauseIcon) {
        playIcon.classList.remove('hidden');
        pauseIcon.classList.add('hidden');
    }

    isPlaying = false;
    togglePlay();
}

function togglePlay() {
    if (!currentTrack) return;

    isPlaying = !isPlaying;
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

    // Here you would typically integrate with your audio playback system
    console.log(`${isPlaying ? 'Playing' : 'Paused'}: ${currentTrack.title}`);
}

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