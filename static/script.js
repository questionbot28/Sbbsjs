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

let isPlaying = false;
let currentProgress = 0;
let progressInterval;

function openPlayer(title, artist, image) {
    document.getElementById("playerTitle").textContent = title;
    document.getElementById("playerArtist").textContent = artist;
    document.getElementById("playerImage").src = image;
    document.getElementById("playerOverlay").style.display = "flex";

    // Reset progress
    currentProgress = 0;
    document.querySelector('.progress').style.width = '0%';
    document.getElementById('currentTime').textContent = '0:00';
    document.getElementById('duration').textContent = '3:30'; // Example duration

    // Reset play button
    document.getElementById('playPauseBtn').textContent = '▶';
    isPlaying = false;
    if (progressInterval) clearInterval(progressInterval);
}

function closePlayer() {
    document.getElementById("playerOverlay").style.display = "none";
    if (progressInterval) clearInterval(progressInterval);
    isPlaying = false;
}

function togglePlay() {
    const playPauseBtn = document.getElementById('playPauseBtn');
    isPlaying = !isPlaying;

    if (isPlaying) {
        playPauseBtn.textContent = '⏸';
        startProgress();
    } else {
        playPauseBtn.textContent = '▶';
        if (progressInterval) clearInterval(progressInterval);
    }
}

function startProgress() {
    if (progressInterval) clearInterval(progressInterval);

    const totalDuration = 210; // 3:30 in seconds
    const progressBar = document.querySelector('.progress');
    const currentTimeElement = document.getElementById('currentTime');

    progressInterval = setInterval(() => {
        if (currentProgress < totalDuration) {
            currentProgress++;
            const percentage = (currentProgress / totalDuration) * 100;
            progressBar.style.width = `${percentage}%`;
            currentTimeElement.textContent = formatTime(currentProgress);
        } else {
            clearInterval(progressInterval);
            isPlaying = false;
            document.getElementById('playPauseBtn').textContent = '▶';
            currentProgress = 0;
        }
    }, 1000);
}

function formatTime(seconds) {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
}

function setupEventListeners() {
    // Search functionality
    const searchBar = document.getElementById('searchBar');
    searchBar.addEventListener('keyup', function(e) {
        if (e.key === 'Enter') {
            searchSongs(this.value);
        }
    });

    // Progress bar click handling
    const progressBar = document.querySelector('.progress-bar');
    progressBar.addEventListener('click', function(e) {
        const rect = this.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const percentage = x / rect.width;

        currentProgress = Math.floor(percentage * 210); // 3:30 in seconds
        document.querySelector('.progress').style.width = `${percentage * 100}%`;
        document.getElementById('currentTime').textContent = formatTime(currentProgress);

        if (isPlaying) startProgress();
    });

    // Volume control
    const volumeSlider = document.querySelector('.volume-slider');
    volumeSlider.addEventListener('input', function() {
        updateVolume(this.value);
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
        // TODO: Replace with actual API call
        const results = [
            { title: "295", artist: "Sidhu Moose Wala", image: "https://i.scdn.co/image/ab67616d0000b273e6f407c7f3a0ec98845e4431" },
            { title: "Dollar", artist: "Sidhu Moose Wala", image: "https://i.scdn.co/image/ab67616d0000b273e7a913a1b83367de2c540088" }
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

function updateVolume(value) {
    console.log(`Volume set to: ${value}%`);
    // TODO: Implement actual volume control
}

function previousTrack() {
    console.log('Previous track');
    // TODO: Implement previous track functionality
}

function nextTrack() {
    console.log('Next track');
    // TODO: Implement next track functionality
}