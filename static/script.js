document.addEventListener("DOMContentLoaded", function() {
    initializeUI();
});

function initializeUI() {
    fetchTrendingSongs();
    fetchRecommendedSongs();
    setupEventListeners();
}

async function fetchTrendingSongs() {
    const trending = document.getElementById("trending-songs");
    try {
        trending.innerHTML = '<div class="loading">Loading trending songs...</div>';
        const response = await fetch('/api/trending');
        if (!response.ok) throw new Error('Failed to fetch trending songs');

        const trendingSongs = await response.json();
        if (trendingSongs.length === 0) {
            trending.innerHTML = '<div class="error">No trending songs available</div>';
            return;
        }

        trending.innerHTML = trendingSongs.map(song => createSongCard(song)).join('');
    } catch (error) {
        console.error("Error fetching trending songs:", error);
        trending.innerHTML = '<div class="error">Failed to load trending songs</div>';
    }
}

async function fetchRecommendedSongs() {
    const recommended = document.getElementById("recommended-songs");
    try {
        recommended.innerHTML = '<div class="loading">Loading recommended songs...</div>';
        // For now, we'll use the same trending endpoint for recommendations
        const response = await fetch('/api/trending');
        if (!response.ok) throw new Error('Failed to fetch recommended songs');

        const recommendedSongs = await response.json();
        if (recommendedSongs.length === 0) {
            recommended.innerHTML = '<div class="error">No recommended songs available</div>';
            return;
        }

        // Shuffle the array to get different songs than trending
        const shuffled = [...recommendedSongs].sort(() => Math.random() - 0.5);
        recommended.innerHTML = shuffled.map(song => createSongCard(song)).join('');
    } catch (error) {
        console.error("Error fetching recommended songs:", error);
        recommended.innerHTML = '<div class="error">Failed to load recommended songs</div>';
    }
}

function getYouTubeThumbnail(videoId) {
    return `https://img.youtube.com/vi/${videoId}/hqdefault.jpg`;
}

function createSongCard(song) {
    const thumbnailUrl = getYouTubeThumbnail(song.videoId);
    return `
        <div class="song-card" onclick="openPlayer('${song.title}', '${song.artist}', '${thumbnailUrl}')">
            <img src="${thumbnailUrl}" alt="${song.title}" onerror="this.src='https://via.placeholder.com/150?text=No+Thumbnail';">
            <p>${song.title}</p>
            <p class="artist">${song.artist}</p>
        </div>
    `;
}

let isPlaying = false;

function openPlayer(title, artist, image) {
    document.getElementById("playerTitle").textContent = title;
    document.getElementById("playerArtist").textContent = artist;
    document.getElementById("playerImage").src = image;
    document.getElementById("playerOverlay").style.display = "flex";

    // Reset play button
    document.getElementById('playPauseBtn').textContent = '▶';
    isPlaying = false;
}

function closePlayer() {
    document.getElementById("playerOverlay").style.display = "none";
    isPlaying = false;
}

function togglePlay() {
    const playPauseBtn = document.getElementById('playPauseBtn');
    isPlaying = !isPlaying;
    playPauseBtn.textContent = isPlaying ? '⏸' : '▶';
}

function setupEventListeners() {
    // Search functionality
    const searchBar = document.getElementById('searchBar');
    searchBar.addEventListener('keyup', function(e) {
        if (e.key === 'Enter') {
            searchSongs(this.value);
        }
    });
}

async function searchSongs(query) {
    console.log(`Searching for: ${query}`);
    const searchResults = document.getElementById('search-results');
    const searchSection = document.getElementById('searchResults');

    // Show search section
    searchSection.style.display = 'block';
    searchResults.innerHTML = '<div class="loading">Searching...</div>';

    try {
        // TODO: Replace with actual YouTube API search
        const response = await fetch('/api/trending');
        if (!response.ok) throw new Error('Failed to fetch songs');

        const songs = await response.json();
        const results = songs.filter(song => 
            song.title.toLowerCase().includes(query.toLowerCase()) ||
            song.artist.toLowerCase().includes(query.toLowerCase())
        );

        if (results.length > 0) {
            searchResults.innerHTML = results.map(song => createSongCard(song)).join('');
        } else {
            searchResults.innerHTML = '<div class="error">No songs found</div>';
        }
    } catch (error) {
        console.error("Error searching songs:", error);
        searchResults.innerHTML = '<div class="error">Error searching songs</div>';
    }
}

function previousTrack() {
    console.log('Previous track');
}

function nextTrack() {
    console.log('Next track');
}