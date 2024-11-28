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
    
        

