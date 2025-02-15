document.addEventListener("DOMContentLoaded", function() {
    // Fetch trending & recommended songs from YouTube
    fetchTrendingSongs();
    fetchRecommendedSongs();
});

function fetchTrendingSongs() {
    let trending = document.getElementById("trending-songs");
    trending.innerHTML = `
        <div class="song-card" onclick="openPlayer('Shape of You', 'Ed Sheeran', 'song1.jpg')">
            <img src="https://via.placeholder.com/180" alt="Song Image">
            <p>Shape of You - Ed Sheeran</p>
        </div>
        <div class="song-card" onclick="openPlayer('Blinding Lights', 'The Weeknd', 'song2.jpg')">
            <img src="https://via.placeholder.com/180" alt="Song Image">
            <p>Blinding Lights - The Weeknd</p>
        </div>
        <div class="song-card" onclick="openPlayer('Stay', 'Kid Laroi & Justin Bieber', 'song3.jpg')">
            <img src="https://via.placeholder.com/180" alt="Song Image">
            <p>Stay - Kid Laroi & Justin Bieber</p>
        </div>
        <div class="song-card" onclick="openPlayer('Bad Guy', 'Billie Eilish', 'song4.jpg')">
            <img src="https://via.placeholder.com/180" alt="Song Image">
            <p>Bad Guy - Billie Eilish</p>
        </div>
        <div class="song-card" onclick="openPlayer('Good 4 U', 'Olivia Rodrigo', 'song5.jpg')">
            <img src="https://via.placeholder.com/180" alt="Song Image">
            <p>Good 4 U - Olivia Rodrigo</p>
        </div>
    `;
}

function fetchRecommendedSongs() {
    let recommended = document.getElementById("recommended-songs");
    recommended.innerHTML = `
        <div class="song-card" onclick="openPlayer('As It Was', 'Harry Styles', 'song6.jpg')">
            <img src="https://via.placeholder.com/180" alt="Song Image">
            <p>As It Was - Harry Styles</p>
        </div>
        <div class="song-card" onclick="openPlayer('Anti-Hero', 'Taylor Swift', 'song7.jpg')">
            <img src="https://via.placeholder.com/180" alt="Song Image">
            <p>Anti-Hero - Taylor Swift</p>
        </div>
        <div class="song-card" onclick="openPlayer('About Damn Time', 'Lizzo', 'song8.jpg')">
            <img src="https://via.placeholder.com/180" alt="Song Image">
            <p>About Damn Time - Lizzo</p>
        </div>
        <div class="song-card" onclick="openPlayer('Heat Waves', 'Glass Animals', 'song9.jpg')">
            <img src="https://via.placeholder.com/180" alt="Song Image">
            <p>Heat Waves - Glass Animals</p>
        </div>
        <div class="song-card" onclick="openPlayer('Shivers', 'Ed Sheeran', 'song10.jpg')">
            <img src="https://via.placeholder.com/180" alt="Song Image">
            <p>Shivers - Ed Sheeran</p>
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