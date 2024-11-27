import os
import requests
import urllib.parse
from flask import Blueprint, redirect, request, session, jsonify, render_template
from datetime import datetime

spotify_blueprint = Blueprint('spotify', __name__)

# The following code sets up the necessary environment variables and URLs for the Spotify API.
S_CLIENT_ID = os.getenv('SPOTIPY_CLIENT_ID')
S_CLIENT_SECRET = os.getenv('SPOTIPY_CLIENT_SECRET')
REDIRECT_URI = 'http://localhost:5000/callback'
AUTH_URL = 'https://accounts.spotify.com/authorize'
TOKEN_URL = 'https://accounts.spotify.com/api/token'
API_BASE_URL = 'https://api.spotify.com/v1/'

@spotify_blueprint.route('/')
def index():
    return "Welcome to Spot to Tube <a href='/login'>Login with Spotify</a>"

@spotify_blueprint.route('/login')
def login():
    scope = 'user-read-private user-read-email'
    parameters = {
        'client_id': S_CLIENT_ID,
        'response_type': 'code',
        'scope': scope,
        'redirect_uri': REDIRECT_URI,
        'show_dialog': True
    }
    auth_url = f"{AUTH_URL}?{urllib.parse.urlencode(parameters)}"
    return redirect(auth_url)

@spotify_blueprint.route('/callback')
def callback():
    if 'error' in request.args:
        return jsonify({"error": request.args['error']})
    if 'code' in request.args:
        req_body = {
            'code': request.args['code'],
            'grant_type': 'authorization_code',
            'redirect_uri': REDIRECT_URI,
            'client_id': S_CLIENT_ID,
            'client_secret': S_CLIENT_SECRET
        }
        response = requests.post(TOKEN_URL, data=req_body)
        token_info = response.json()
        session['access_token'] = token_info['access_token']
        session['refresh_token'] = token_info['refresh_token']
        session['expires_at'] = datetime.now().timestamp() + token_info['expires_in']
        return redirect('/playlists')

@spotify_blueprint.route('/playlists')
def get_playlists():
    if 'access_token' not in session:
        return redirect('/spotify/login')

    if datetime.now().timestamp() > session['expires_at']:
        return redirect('/spotify/refresh-token')

    headers = {
        'Authorization': f"Bearer {session['access_token']}"
    }

    response = requests.get(f"{API_BASE_URL}me/playlists", headers=headers)
    playlists = response.json().get('items', [])
    
    return render_template('playlists.html', playlists=playlists)

@spotify_blueprint.route('/refresh-token')
def refresh_token():
    if 'refresh_token' not in session:
        return redirect('/login')
    
    if datetime.now().timestamp() > session['expires_at']:
        req_body = {
            'grant_type': 'refresh_token',
            'refresh_token': session['refresh_token'],
            'client_id': S_CLIENT_ID,
            'client_secret': S_CLIENT_SECRET
        }
        response = requests.post(TOKEN_URL, data=req_body)
        new_token_info = response.json()
        session['access_token'] = new_token_info['access_token']
        session['expires_at'] = datetime.now().timestamp() + new_token_info['expires_in']
        return redirect('/playlists') 