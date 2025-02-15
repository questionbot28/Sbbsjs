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
        const trendingSongs = [
            { title: "Ryde or Die", artist: "Chinna, Manni Sandhu, Karam Brar", videoId: "YxWlaYCA8MU" },
            { title: "Gandasa", artist: "Jassa Dhillon, Karam Brar", videoId: "lq_ZdzHG_8k" },
            { title: "295", artist: "Sidhu Moose Wala", videoId: "n_FCrCQ6-bA" },
            { title: "Same Beef", artist: "Bohemia, Sidhu Moose Wala", videoId: "iC0hovmu1rw" },
            { title: "Dollar", artist: "Sidhu Moose Wala", videoId: "87xE4s2gZ0k" }
        ];

        trending.innerHTML = trendingSongs.map(song => createSongCard(song)).join('');
    } catch (error) {
        console.error("Error fetching trending songs:", error);
        trending.innerHTML = '<div class="error">Failed to load trending songs</div>';
    }
}

async function fetchRecommendedSongs() {
    const recommended = document.getElementById("recommended-songs");
    try {
        const recommendedSongs = [
            { title: "Machreya", artist: "Gulab Sidhu, Diamond", videoId: "D2QYyr9tF70" },
            { title: "Baller", artist: "Shubh", videoId: "6wkWBxMtKic" },
            { title: "Excuses", artist: "AP Dhillon, Gurinder Gill", videoId: "vX2cDW8LUWk" },
            { title: "Brown Munde", artist: "AP Dhillon", videoId: "VNwah1GtYrk" },
            { title: "Elevated", artist: "Shubh", videoId: "BM8B1Xp0BG8" }
        ];

        recommended.innerHTML = recommendedSongs.map(song => createSongCard(song)).join('');
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
        // Sample search results with actual video IDs
        const results = [
            { title: "295", artist: "Sidhu Moose Wala", videoId: "n_FCrCQ6-bA" },
            { title: "Dollar", artist: "Sidhu Moose Wala", videoId: "87xE4s2gZ0k" }
        ].filter(song => 
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