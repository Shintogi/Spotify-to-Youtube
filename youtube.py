import os
import json
import requests
import urllib.parse
from flask import Blueprint, redirect, request, session, jsonify

youtube_blueprint = Blueprint('youtube', __name__)

# load env variables
Y_Client_ID = os.getenv('YOUTUBE_CLIENT_ID')
Y_Client_Secret = os.getenv('YOUTUBE_CLIENT_SECRET')
REDIRECT_URI = 'http://localhost:5000/youtube/callback'
AUTH_URL = 'https://accounts.google.com/o/oauth2/auth'
TOKEN_URL = 'https://oauth2.googleapis.com/token'
API_BASE_URL = 'https://www.googleapis.com/youtube/v3/'

@youtube_blueprint.route('/logout')
def youtube_logout():
    # Clear YouTube-specific session data
    session.pop('yt_access_token', None)
    session.pop('yt_refresh_token', None)
    
    # Redirect to Google's logout URL and then back to our app
    return f'''
        <h2>Logging out of YouTube...</h2>
        <script>
            // Clear Google's auth cookies
            window.location.href = "https://accounts.google.com/logout?continue=https://www.youtube.com&redirect_to={request.host_url}";
        </script>
    '''

@youtube_blueprint.route('/login')
def youtube_login():
    # Clear any existing YouTube tokens before new login
    session.pop('yt_access_token', None)
    session.pop('yt_refresh_token', None)
    
    # defining scope
    scope = 'https://www.googleapis.com/auth/youtube.force-ssl'
    parameters = {
        'client_id': Y_Client_ID,
        'redirect_uri': REDIRECT_URI,
        'response_type': 'code',
        'scope': scope,
        'access_type': 'offline',
        'prompt': 'select_account consent'  # Added select_account to force account picker
    }
    
    auth_url = f"{AUTH_URL}?{urllib.parse.urlencode(parameters)}"
    return redirect(auth_url)

@youtube_blueprint.route('/callback')
def youtube_callback():
    if 'error' in request.args:
        return jsonify({"error": request.args['error']})
    if 'code' in request.args:
        req_body = {
            'code': request.args['code'],
            'grant_type': 'authorization_code',
            'redirect_uri': REDIRECT_URI,
            'client_id': Y_Client_ID,
            'client_secret': Y_Client_Secret,
        }
        response = requests.post(TOKEN_URL, data=req_body)
        token_info = response.json()
        session['yt_access_token'] = token_info.get('access_token')
        session['yt_refresh_token'] = token_info.get('refresh_token')
        return redirect('/youtube/create_playlist')

@youtube_blueprint.route('/create_playlist', methods=['GET', 'POST'])
def create_youtube_playlist():
    if 'yt_access_token' not in session:
        return redirect('/youtube/login')
    
    if request.method == 'GET':
        return '''
        <div style="margin: 20px;">
            <div style="text-align: right;">
                <a href="/youtube/logout" style="color: red; text-decoration: none;">Switch YouTube Account</a>
            </div>
            <form method="post">
                <label>Playlist Name:</label><br>
                <input type="text" name="playlist_name" required><br><br>
                <label>Description:</label><br>
                <textarea name="description"></textarea><br><br>
                <label>Privacy:</label><br>
                <select name="privacy_status">
                    <option value="private">Private</option>
                    <option value="unlisted">Unlisted</option>
                    <option value="public">Public</option>
                </select><br><br>
                <button type="submit">Create Playlist</button>
            </form>
        </div>
        '''
    elif request.method == 'POST':
        playlist_name = request.form.get('playlist_name')
        playlist_description = request.form.get('description', '')
        playlist_privacy_status = request.form.get('privacy_status', 'private')
        
        headers = {
            'Authorization': f"Bearer {session['yt_access_token']}",
            'Content-Type': 'application/json'
        }
        
        request_body = {
            'snippet': {
                'title': playlist_name,
                'description': playlist_description
            },
            'status': {
                'privacyStatus': playlist_privacy_status
            }
        }
        
        response = requests.post(
            f"{API_BASE_URL}playlists?part=snippet,status",
            headers=headers,
            json=request_body
        )
        
        if response.status_code == 401 and "youtubeSignupRequired" in response.text:
            return '''
                <h2>YouTube Channel Required</h2>
                <p>To create a playlist, you need a YouTube channel. Please follow these steps:</p>
                <ol>
                    <li>Open <a href="https://www.youtube.com/create_channel" target="_blank">YouTube Channel Creation</a> in a new tab</li>
                    <li>Create your channel</li>
                    <li>Return here and <a href="/youtube/login">click here to try again</a></li>
                </ol>
            '''
        
        if response.status_code == 200:
            playlist_data = response.json()
            youtube_playlist_id = playlist_data['id']
            
            # Get the Spotify playlist ID from session
            spotify_playlist_id = session.get('pending_playlist_id')
            
            if not spotify_playlist_id:
                return "No Spotify playlist ID found", 400
                
            # Get Spotify tracks
            spotify_headers = {
                'Authorization': f"Bearer {session['access_token']}"
            }
            
            spotify_response = requests.get(
                f"https://api.spotify.com/v1/playlists/{spotify_playlist_id}/tracks",
                headers=spotify_headers
            )
            
            if spotify_response.status_code != 200:
                return "Failed to get Spotify tracks", spotify_response.status_code
                
            tracks = spotify_response.json().get('items', [])
            successful_transfers = 0
            
            # Process each track
            for track in tracks:
                track_name = track['track']['name']
                artists = ', '.join(artist['name'] for artist in track['track']['artists'])
                search_query = f"{track_name} {artists}"
                
                # Search for video
                search_response = requests.get(
                    f"{API_BASE_URL}search?part=snippet&q={search_query}&type=video&key={os.getenv('YOUTUBE_API_KEY')}",
                    headers=headers
                )
                
                if search_response.status_code == 200:
                    search_results = search_response.json().get('items', [])
                    if search_results:
                        video_id = search_results[0]['id']['videoId']
                        # Add video to playlist
                        add_video_response = requests.post(
                            f"{API_BASE_URL}playlistItems?part=snippet",
                            headers=headers,
                            json={
                                'snippet': {
                                    'playlistId': youtube_playlist_id,
                                    'resourceId': {
                                        'kind': 'youtube#video',
                                        'videoId': video_id
                                    }
                                }
                            }
                        )
                        if add_video_response.status_code == 200:
                            successful_transfers += 1
            
            return f'''
                <h2>Success!</h2>
                <p>Playlist '{playlist_name}' created successfully!</p>
                <p>Successfully transferred {successful_transfers} out of {len(tracks)} tracks.</p>
                <p>View your playlist: <a href="https://www.youtube.com/playlist?list={youtube_playlist_id}" target="_blank">Open in YouTube</a></p>
                <p><a href="/">Back to Home</a></p>
                '''
        else:
            error_message = f"Failed to create playlist. Status code: {response.status_code}"
            if response.text:
                try:
                    error_info = response.json()
                    error_message += f"\nError details: {error_info}"
                except:
                    error_message += f"\nResponse text: {response.text}"
            return error_message, response.status_code



