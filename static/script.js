document.addEventListener("DOMContentLoaded", function() {
    // Initialize the web UI
    initializeUI();
});

function initializeUI() {
    // Fetch trending & recommended songs
    fetchTrendingSongs();
    fetchRecommendedSongs();

    // Set up event listeners
    setupEventListeners();
}

async function fetchTrendingSongs() {
    const trending = document.getElementById("trending-songs");
    try {
        // Temporary static data until backend is connected
        const trendingSongs = [
            { title: "Shape of You", artist: "Ed Sheeran", image: "https://via.placeholder.com/180" },
            { title: "Blinding Lights", artist: "The Weeknd", image: "https://via.placeholder.com/180" },
            { title: "Stay", artist: "Kid Laroi & Justin Bieber", image: "https://via.placeholder.com/180" },
            { title: "Bad Guy", artist: "Billie Eilish", image: "https://via.placeholder.com/180" },
            { title: "Good 4 U", artist: "Olivia Rodrigo", image: "https://via.placeholder.com/180" }
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
        // Temporary static data until backend is connected
        const recommendedSongs = [
            { title: "As It Was", artist: "Harry Styles", image: "https://via.placeholder.com/180" },
            { title: "Anti-Hero", artist: "Taylor Swift", image: "https://via.placeholder.com/180" },
            { title: "About Damn Time", artist: "Lizzo", image: "https://via.placeholder.com/180" },
            { title: "Heat Waves", artist: "Glass Animals", image: "https://via.placeholder.com/180" },
            { title: "Shivers", artist: "Ed Sheeran", image: "https://via.placeholder.com/180" }
        ];

        recommended.innerHTML = recommendedSongs.map(song => createSongCard(song)).join('');
    } catch (error) {
        console.error("Error fetching recommended songs:", error);
        recommended.innerHTML = '<div class="error">Failed to load recommended songs</div>';
    }
}

function createSongCard(song) {
    return `
        <div class="song-card" onclick="openPlayer('${song.title}', '${song.artist}', '${song.image}')">
            <img src="${song.image}" alt="${song.title}">
            <p>${song.title} - ${song.artist}</p>
        </div>
    `;
}

function openPlayer(title, artist, image) {
    document.getElementById("playerTitle").textContent = title;
    document.getElementById("playerArtist").textContent = artist;
    document.getElementById("playerImage").src = image;
    document.getElementById("playerOverlay").style.display = "flex";
}

function closePlayer() {
    document.getElementById("playerOverlay").style.display = "none";
}

function setupEventListeners() {
    // Navigation buttons
    document.querySelectorAll('.nav-btn').forEach(button => {
        button.addEventListener('click', function() {
            document.querySelectorAll('.nav-btn').forEach(btn => 
                btn.classList.remove('active'));
            this.classList.add('active');
        });
    });

    // Search functionality
    document.getElementById('searchBar').addEventListener('keyup', function(e) {
        if (e.key === 'Enter') {
            searchSongs(this.value);
        }
    });

    // Volume slider
    const volumeSlider = document.querySelector('.volume-slider');
    if (volumeSlider) {
        volumeSlider.addEventListener('input', function() {
            updateVolume(this.value);
        });
    }
}

function searchSongs(query) {
    console.log(`Searching for: ${query}`);
    // TODO: Implement actual search functionality
}

function updateVolume(value) {
    console.log(`Volume set to: ${value}%`);
    // TODO: Implement volume control
}

function togglePlay() {
    const playPauseBtn = document.getElementById('playPauseBtn');
    if (playPauseBtn.textContent === '▶') {
        playPauseBtn.textContent = '⏸';
    } else {
        playPauseBtn.textContent = '▶';
    }
}

function nextTrack() {
    console.log('Next track');
    // TODO: Implement next track functionality
}

function previousTrack() {
    console.log('Previous track');
    // TODO: Implement previous track functionality
}