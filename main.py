import http
import os
import json
import requests
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
import urllib.parse
from flask import Flask, redirect, request, jsonify, session
from dotenv import load_dotenv
from datetime import datetime, timedelta
from flask import render_template
app = Flask(__name__)

app.secret_key = 'q8BX2vUR@IQNIrN6ajL9OkZLR3%y9rtaLsD'

#load env for client id and secret
load_dotenv()

S_CLIENT_ID = os.getenv('SPOTIPY_CLIENT_ID')
S_CLIENT_SECRET = os.getenv('SPOTIPY_CLIENT_SECRET')
REDIRECT_URI = 'http://localhost:5000/callback'

AUTH_URL = 'https://accounts.spotify.com/authorize'
TOKEN_URL = 'https://accounts.spotify.com/api/token'
API_BASE_URL = 'https://api.spotify.com/v1/'

@app.route('/')
def index():
    return "Welcome to Spot to Tube <a href='/login'>Login with Spotify</a>"

#endpoint to redirect to spot login page
@app.route('/login')
def login():
    scope = 'user-read-private user-read-email'


    parameters = {
        'client_id' : S_CLIENT_ID,
        'response_type': 'code',
        'scope' : scope,
        'redirect_uri': REDIRECT_URI,
        'show_dialog' : True #to make me(Denzel) login in everytime for testing
    }

    auth_url = f"{AUTH_URL}?{urllib.parse.urlencode(parameters)}"
    return redirect(auth_url)

#Callback endpoint

@app.route('/callback')
def callback():
    #in case there is a login error
    if 'error' in request.args:
        return jsonify({"error" : request.args['error']})
    #sucessfull login
    if 'code' in request.args:
        req_body = {
            'code' : request.args['code'],
            'grant_type': 'authorization_code',
            'redirect_uri':  REDIRECT_URI,
            'client_id': S_CLIENT_ID,
            'client_secret': S_CLIENT_SECRET
        }
    reponse = requests.post(TOKEN_URL, data=req_body)
    token_info = reponse.json()

    session['access_token'] = token_info['access_token']
    session['refresh_token'] = token_info['refresh_token'] #revirifies the access token that is needed to "access" client information
    session['expires_at'] = datetime.now().timestamp() + token_info['expires_in'] #timestamp thjat tells excatly when the access token expires

    return redirect('/playlists')

@app.route('/playlists')

def get_playlists():
    if 'access_token' not in session:
        return redirect('/login')
    
    #checking that the access token has not expired || if expired we will redirect to refresh the token
    if datetime.now().timestamp() > session['expires_at']:
        return('/refresh-token')
    
    headers = {
         'Authorization': f"Bearer {session['access_token']}"
     }
    
    response = requests.get(f"{API_BASE_URL}me/playlists", headers=headers)
    playlists = response.json()['items']
    
    return jsonify(playlists)

#searching for a specific playlist
def search_playlist(playlist_id):
    playlist_name = request.form['playlist_id']

    if 'access_token' not in session:
        return redirect('/login')
    
    if datetime.now().timestamp() > session['expires_at']:
        return redirect('/refresh-token')
    
    #search for playlists with specific name
    headers = {
        'Authorization': f"Bearer {session['access_token']}"
    }
    query_params = {
        'q': playlist_name,
        'type': 'playlist',
    }

    reponse = request.get(f"{http://api.spotify.com/v1/}", headers = headers, params=query_params)
    search_playlist = reponse.json().get('playlists', {}).get('items', [])

    return render_template('playlists.html', playlists=search_playlist)
#refresh access token when/if expired
    
app.route('/refresh-token')
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
        session['expires_at'] = datetime.now().timestamp + new_token_info['expires_in']

        return redirect('/playlists')
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)

# Getting youtube access token


# Authorizing youtube api

    


