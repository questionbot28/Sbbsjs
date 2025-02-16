import os
from flask import Blueprint, redirect, request, url_for, session, current_app
from flask_login import LoginManager, login_user, logout_user, current_user
from models import User, users
import requests
from uuid import uuid4

auth = Blueprint('auth', __name__)
login_manager = LoginManager()

DISCORD_CLIENT_ID = os.getenv('DISCORD_CLIENT_ID')
DISCORD_CLIENT_SECRET = os.getenv('DISCORD_CLIENT_SECRET')
DISCORD_REDIRECT_URI = f'https://{os.getenv("REPL_SLUG")}.{os.getenv("REPL_OWNER")}.repl.co/callback'
DISCORD_API_ENDPOINT = 'https://discord.com/api/v10'

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

@auth.route('/login')
def login():
    return redirect(f'https://discord.com/api/oauth2/authorize?client_id={DISCORD_CLIENT_ID}'
                   f'&redirect_uri={DISCORD_REDIRECT_URI}&response_type=code&scope=identify')

@auth.route('/callback')
def callback():
    code = request.args.get('code')
    data = {
        'client_id': DISCORD_CLIENT_ID,
        'client_secret': DISCORD_CLIENT_SECRET,
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': DISCORD_REDIRECT_URI,
        'scope': 'identify'
    }
    
    # Exchange code for token
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    token_response = requests.post(f'{DISCORD_API_ENDPOINT}/oauth2/token', data=data, headers=headers)
    
    if token_response.status_code != 200:
        return 'Failed to get access token', 400
        
    token_data = token_response.json()
    access_token = token_data['access_token']
    
    # Get user info
    headers = {'Authorization': f'Bearer {access_token}'}
    user_response = requests.get(f'{DISCORD_API_ENDPOINT}/users/@me', headers=headers)
    
    if user_response.status_code != 200:
        return 'Failed to get user info', 400
        
    user_data = user_response.json()
    
    # Create or update user
    user_id = str(uuid4())
    user = {
        'id': user_id,
        'username': user_data['username'],
        'discord_id': user_data['id'],
        'avatar': f'https://cdn.discordapp.com/avatars/{user_data["id"]}/{user_data["avatar"]}.png' if user_data.get('avatar') else None
    }
    users[user_id] = user
    
    user_obj = User(**user)
    login_user(user_obj)
    
    return redirect(url_for('index'))

@auth.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))
