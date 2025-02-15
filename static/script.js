document.addEventListener("DOMContentLoaded", function() {
    // Fetch trending & recommended songs from YouTube
    fetchTrendingSongs();
    fetchRecommendedSongs();
});

function fetchTrendingSongs() {
    let trending = document.getElementById("trending-songs");
    trending.innerHTML = `
        <div class="song" onclick="playSong('Song 1', 'Artist 1', 'song1.mp3')">
            <img src="https://via.placeholder.com/180" alt="Thumbnail">
            <p>Song 1 - Artist 1</p>
        </div>
        <div class="song" onclick="playSong('Song 2', 'Artist 2', 'song2.mp3')">
            <img src="https://via.placeholder.com/180" alt="Thumbnail">
            <p>Song 2 - Artist 2</p>
        </div>
    `;
}

function fetchRecommendedSongs() {
    let recommended = document.getElementById("recommended-songs");
    recommended.innerHTML = `
        <div class="song" onclick="playSong('Song 3', 'Artist 3', 'song3.mp3')">
            <img src="https://via.placeholder.com/180" alt="Thumbnail">
            <p>Song 3 - Artist 3</p>
        </div>
        <div class="song" onclick="playSong('Song 4', 'Artist 4', 'song4.mp3')">
            <img src="https://via.placeholder.com/180" alt="Thumbnail">
            <p>Song 4 - Artist 4</p>
        </div>
    `;
}

function playSong(title, artist, audioSrc) {
    document.getElementById("song-title").textContent = title;
    document.getElementById("song-artist").textContent = artist;
    document.getElementById("audio-player").src = audioSrc;
    document.getElementById("song-thumbnail").src = "https://via.placeholder.com/60";

    document.getElementById("music-player").classList.remove("hidden");
}

// Navigation handling
document.querySelectorAll('.nav-options span').forEach(span => {
    span.addEventListener('click', function() {
        // Remove active class from all spans
        document.querySelectorAll('.nav-options span').forEach(s => 
            s.classList.remove('active'));
        // Add active class to clicked span
        this.classList.add('active');
        
        // Handle navigation (can be expanded later)
        console.log(`Navigated to ${this.id}`);
    });
});

// Search handling
document.getElementById('search').addEventListener('keyup', function(e) {
    if (e.key === 'Enter') {
        console.log(`Searching for: ${this.value}`);
        // TODO: Implement search functionality
    }
});
