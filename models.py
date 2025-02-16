from flask_login import UserMixin
from datetime import datetime

class User(UserMixin):
    def __init__(self, id, username, discord_id, avatar=None):
        self.id = id
        self.username = username
        self.discord_id = discord_id
        self.avatar = avatar
        self.created_at = datetime.utcnow()
        self.liked_songs = set()  # Store liked song IDs
        
    @staticmethod
    def get(user_id):
        # In a real app, this would fetch from database
        # For now, we'll use a simple in-memory storage
        if user_id in users:
            return User(**users[user_id])
        return None

# In-memory storage (replace with database in production)
users = {}
