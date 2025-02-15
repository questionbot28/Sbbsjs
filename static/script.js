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
            { title: "Shape of You", artist: "Ed Sheeran", image: "https://i.scdn.co/image/ab67616d0000b273ba5db46f4b838ef6027e6f96" },
            { title: "Blinding Lights", artist: "The Weeknd", image: "https://i.scdn.co/image/ab67616d0000b2738863bc11d2aa12b54f5aeb36" },
            { title: "Stay", artist: "Kid Laroi & Justin Bieber", image: "https://i.scdn.co/image/ab67616d0000b273e85259a1cae29a8d91f2093d" },
            { title: "Bad Guy", artist: "Billie Eilish", image: "https://i.scdn.co/image/ab67616d0000b2732a038d3bf875d23e4aeaa84e" },
            { title: "Good 4 U", artist: "Olivia Rodrigo", image: "https://i.scdn.co/image/ab67616d0000b273a91c10fe9472d9bd89802e5a" }
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
            { title: "As It Was", artist: "Harry Styles", image: "https://i.scdn.co/image/ab67616d0000b2732e8ed79e177ff6011076f5f0" },
            { title: "Anti-Hero", artist: "Taylor Swift", image: "https://i.scdn.co/image/ab67616d0000b273bb54dde68cd23e2a268ae0f5" },
            { title: "About Damn Time", artist: "Lizzo", image: "https://i.scdn.co/image/ab67616d0000b273b56f0e5a7eac1c1dda144acd" },
            { title: "Heat Waves", artist: "Glass Animals", image: "https://i.scdn.co/image/ab67616d0000b2739e495fb707973f3390850eea" },
            { title: "Shivers", artist: "Ed Sheeran", image: "https://i.scdn.co/image/ab67616d0000b273ef24c3fdbf856340d55cfeb2" }
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
            <img src="${song.image}" alt="${song.title}" onerror="this.src='https://community.spotify.com/t5/image/serverpage/image-id/55829iC2AD64ADB887E2A5';">
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