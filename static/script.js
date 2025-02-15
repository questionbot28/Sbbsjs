document.addEventListener("DOMContentLoaded", function() {
    // Fetch trending & recommended songs from YouTube
    fetchTrendingSongs();
    fetchRecommendedSongs();
});

function fetchTrendingSongs() {
    let trending = document.getElementById("trending-songs");
    trending.innerHTML = `
        <div class="song">
            <img src="https://via.placeholder.com/180" alt="Thumbnail">
            <p>Song 1 - Artist 1</p>
        </div>
        <div class="song">
            <img src="https://via.placeholder.com/180" alt="Thumbnail">
            <p>Song 2 - Artist 2</p>
        </div>
    `;
}

function fetchRecommendedSongs() {
    let recommended = document.getElementById("recommended-songs");
    recommended.innerHTML = `
        <div class="song">
            <img src="https://via.placeholder.com/180" alt="Thumbnail">
            <p>Song 3 - Artist 3</p>
        </div>
        <div class="song">
            <img src="https://via.placeholder.com/180" alt="Thumbnail">
            <p>Song 4 - Artist 4</p>
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
    document.getElementById("audioPlayer").pause();
}

// Handle navigation button clicks
document.querySelectorAll('.nav-btn').forEach(button => {
    button.addEventListener('click', function() {
        // Remove active class from all buttons
        document.querySelectorAll('.nav-btn').forEach(btn => 
            btn.classList.remove('active'));
        // Add active class to clicked button
        this.classList.add('active');

        console.log(`Navigated to ${this.textContent}`);
    });
});

// Handle search
document.getElementById('searchBar').addEventListener('keyup', function(e) {
    if (e.key === 'Enter') {
        console.log(`Searching for: ${this.value}`);
        // TODO: Implement search functionality
    }
});