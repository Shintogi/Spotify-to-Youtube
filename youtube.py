import os
import json
import requests
import urllib.parse
from flask import Blueprint,redirect,request,session,render_template, jsonify

youtube_blueprint = Blueprint('youtube', __name__)

# load env variables

Y_Client_ID = os.getenv('YOUTUBE_CLIENT_ID')
Y_Client_Secret = os.getenv('YOUTUBE_CLIENT_SECRET')
REDIRECT_URI = 'http://localhost:5000/youtube/callback'
AUTH_URL = 'https://accounts.google.com/o/oauth2/auth'
TOKEN_URL = 'https://oauth2.googleapis.com/token'
API_BASE_URL = 'https://www.googleapis.com/youtube/v3/'

@youtube_blueprint.route('/youtube/login')
def youtube_login():
    # defining scope
    scope = 'https://www.googleapis.com/auth/youtube.force-ssl'
    parameters = {
        'client_id': Y_Client_ID,
        'client_secret': Y_Client_Secret,
        'response_type' : 'code',
        'scope' : scope,
        'access_type' : 'offline',
        'prompt' : 'consent'

    }
    #Redirect users to OAUTH consent screen
    AUTH_URL =  f"{AUTH_URL}?{urllib.parse.urlencode(parameters)}"
    return redirect(AUTH_URL)

    #youtube callback with 'code'
@youtube_blueprint.route('/youtube/callback')
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

# main playlists functionality
@youtube_blueprint.route('/youtube/create_playlists', methods = ['GET', 'POST']) # it is supposed to display a form to get playlist details such as names and description
def create_youtube_playlist():
        if 'yt_access_token' not in session:
            return redirect('/youtube/login')  # Redirect to login if token is missing
        
        if request.method == 'GET':
            #Display a way for usuers to input playlist specifications
            return '''
            <form method="post">
                <label>Playlist Name:</label><br>
                <input type="text" name="playlist_name" required><br><br>
                <label>Description:</label><br>
                <textarea name="description"></textarea><br><br>
                <label>Privacy:</label><br>
                <select name="privacy_status">
                    <option value="public">Public</option>
                    <option value="private">Private</option>
                    <option value="unlisted">Unlisted</option>
                </select><br><br>
                <button type="submit">Create Playlist</button>
            </form>
        '''
        elif request.method == 'POST':
            #User input
            playlist_name = request.form.get('playlist_name')
            playlist_description = request.form.get('playlist_description')
            playlist_privacy_status = request.form.get('playlist_privacy_status')
            
            
        headers = {
            'Authorization': f"Bearer{session['youtube_access_token']}",
            'Content-Type': 'application/json'
        }
        #request Body // this should grab the main inputs given in the request methods 'GET'
        body = {
            'snippet': {
                'title':playlist_name,
                'description': playlist_description
            },
            'status': {
                'privacy_status': playlist_privacy_status
            }
        }
        
        # Call Yt API to create this playlist
        reponse = requests.post(
            f"{API_BASE_URL}playlist?part=snippet,status",
            headers=headers,
            json=body
        )
        
        #Error handling / debugging
        if reponse.status_code == 200:
            playlist_id = reponse.json()['id']
            return f"Playlist '{playlist_name}' created successfully! Playlist ID: {playlist_id}"
        else:
            error_info = reponse.json()
            return f"Failed to create playlist: {error_info.get('error', {}).get('message', 'Unknown error')}", reponse.status_code
            


    

        

