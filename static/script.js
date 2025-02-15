document.addEventListener("DOMContentLoaded", function() {
    initializeUI();
});

function initializeUI() {
    fetchTrendingSongs();
    fetchNewReleases();
    fetchIndianSongs();
    fetchPunjabiSongs();
    fetchHindiSongs();
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

async function fetchNewReleases() {
    const newReleases = document.getElementById("new-releases");
    try {
        newReleases.innerHTML = '<div class="loading">Loading new releases...</div>';
        const response = await fetch('/api/new-releases');
        if (!response.ok) throw new Error('Failed to fetch new releases');

        const songs = await response.json();
        if (songs.length === 0) {
            newReleases.innerHTML = '<div class="error">No new releases available</div>';
            return;
        }

        newReleases.innerHTML = songs.map(song => createSongCard(song)).join('');
    } catch (error) {
        console.error("Error fetching new releases:", error);
        newReleases.innerHTML = '<div class="error">Failed to load new releases</div>';
    }
}

async function fetchIndianSongs() {
    const indianSongs = document.getElementById("indian-songs");
    try {
        indianSongs.innerHTML = '<div class="loading">Loading Indian songs...</div>';
        const response = await fetch('/api/indian');
        if (!response.ok) throw new Error('Failed to fetch Indian songs');

        const songs = await response.json();
        if (songs.length === 0) {
            indianSongs.innerHTML = '<div class="error">No Indian songs available</div>';
            return;
        }

        indianSongs.innerHTML = songs.map(song => createSongCard(song)).join('');
    } catch (error) {
        console.error("Error fetching Indian songs:", error);
        indianSongs.innerHTML = '<div class="error">Failed to load Indian songs</div>';
    }
}

async function fetchPunjabiSongs() {
    const punjabiSongs = document.getElementById("punjabi-songs");
    try {
        punjabiSongs.innerHTML = '<div class="loading">Loading Punjabi songs...</div>';
        const response = await fetch('/api/punjabi');
        if (!response.ok) throw new Error('Failed to fetch Punjabi songs');

        const songs = await response.json();
        if (songs.length === 0) {
            punjabiSongs.innerHTML = '<div class="error">No Punjabi songs available</div>';
            return;
        }

        punjabiSongs.innerHTML = songs.map(song => createSongCard(song)).join('');
    } catch (error) {
        console.error("Error fetching Punjabi songs:", error);
        punjabiSongs.innerHTML = '<div class="error">Failed to load Punjabi songs</div>';
    }
}

async function fetchHindiSongs() {
    const hindiSongs = document.getElementById("hindi-songs");
    try {
        hindiSongs.innerHTML = '<div class="loading">Loading Hindi songs...</div>';
        const response = await fetch('/api/hindi');
        if (!response.ok) throw new Error('Failed to fetch Hindi songs');

        const songs = await response.json();
        if (songs.length === 0) {
            hindiSongs.innerHTML = '<div class="error">No Hindi songs available</div>';
            return;
        }

        hindiSongs.innerHTML = songs.map(song => createSongCard(song)).join('');
    } catch (error) {
        console.error("Error fetching Hindi songs:", error);
        hindiSongs.innerHTML = '<div class="error">Failed to load Hindi songs</div>';
    }
}

function createSongCard(song) {
    const title = song.title.replace(/'/g, '&#39;');  // Escape single quotes
    const artist = song.artist.replace(/'/g, '&#39;');
    const views = parseInt(song.views).toLocaleString();  // Format view count

    return `
        <div class="song-card" onclick="openPlayer('${title}', '${artist}', '${song.thumbnail}', '${song.videoId}')">
            <img src="${song.thumbnail}" alt="${title}" onerror="this.src='https://via.placeholder.com/150?text=No+Thumbnail';">
            <p class="song-title">${title}</p>
            <p class="artist">${artist}</p>
            <p class="views">👁 ${views} views</p>
        </div>
    `;
}

let isPlaying = false;
let currentVideoId = null;

function openPlayer(title, artist, image, videoId) {
    currentVideoId = videoId;
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
    currentVideoId = null;
}

function togglePlay() {
    const playPauseBtn = document.getElementById('playPauseBtn');
    isPlaying = !isPlaying;
    playPauseBtn.textContent = isPlaying ? '⏸' : '▶';

    // Here you would typically integrate with YouTube's iframe API
    console.log(`${isPlaying ? 'Playing' : 'Paused'} video: ${currentVideoId}`);
}

function setupEventListeners() {
    // Search functionality
    const searchBar = document.getElementById('searchBar');
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

async function searchSongs(query) {
    console.log(`Searching for: ${query}`);
    const searchResults = document.getElementById('search-results');
    const searchSection = document.getElementById('searchResults');

    // Show search section
    searchSection.style.display = 'block';
    searchResults.innerHTML = '<div class="loading">Searching...</div>';

    try {
        const response = await fetch('/api/trending');  // TODO: Replace with actual search endpoint
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

function getYouTubeThumbnail(videoId) {
    return `https://img.youtube.com/vi/${videoId}/hqdefault.jpg`;
}