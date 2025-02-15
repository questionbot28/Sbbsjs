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
            { title: "Ryde or Die", artist: "Chinna, Manni Sandhu, Karam Brar", image: "https://i.scdn.co/image/ab67616d0000b273d6540036d05fb1abf72d4186" },
            { title: "Gandasa", artist: "Jassa Dhillon, Karam Brar", image: "https://i.scdn.co/image/ab67616d0000b273a91c10fe9472d9bd89802e5a" },
            { title: "295", artist: "Sidhu Moose Wala", image: "https://i.scdn.co/image/ab67616d0000b273e6f407c7f3a0ec98845e4431" },
            { title: "Same Beef", artist: "Bohemia, Sidhu Moose Wala", image: "https://i.scdn.co/image/ab67616d0000b273e6b0c0daf8995a7cbb2f9b05" },
            { title: "Dollar", artist: "Sidhu Moose Wala", image: "https://i.scdn.co/image/ab67616d0000b273e7a913a1b83367de2c540088" }
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
            { title: "Machreya", artist: "Gulab Sidhu, Diamond", image: "https://i.scdn.co/image/ab67616d0000b2738863bc11d2aa12b54f5aeb36" },
            { title: "Baller", artist: "Shubh", image: "https://i.scdn.co/image/ab67616d0000b273bb54dde68cd23e2a268ae0f5" },
            { title: "Excuses", artist: "AP Dhillon, Gurinder Gill", image: "https://i.scdn.co/image/ab67616d0000b273b56f0e5a7eac1c1dda144acd" },
            { title: "Brown Munde", artist: "AP Dhillon", image: "https://i.scdn.co/image/ab67616d0000b2739e495fb707973f3390850eea" },
            { title: "Elevated", artist: "Shubh", image: "https://i.scdn.co/image/ab67616d0000b273ef24c3fdbf856340d55cfeb2" }
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
            <p>${song.title}</p>
        </div>
    `;
}

function openPlayer(title, artist, image) {
    document.getElementById("playerTitle").textContent = title;
    document.getElementById("playerArtist").textContent = artist;
    document.getElementById("playerImage").src = image;
    document.getElementById("playerOverlay").style.display = "flex";

    // Reset audio source when opening new song
    const audioPlayer = document.getElementById("audioPlayer");
    audioPlayer.pause();
    // TODO: Set actual audio source when connected to backend
    // audioPlayer.src = audioUrl;
}

function closePlayer() {
    const audioPlayer = document.getElementById("audioPlayer");
    audioPlayer.pause();
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
    // TODO: Implement search functionality
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