from flask import Blueprint, session, request, redirect, url_for
import requests
import os

connector_blueprint = Blueprint('connector', __name__)

def add_to_youtube_playlist(video_id, playlist_id, youtube_headers):
    """Helper function to add videos to playlist"""
    try:
        request_body = {
            'snippet': {
                'playlistId': playlist_id,
                'resourceId': {
                    'kind': 'youtube#video',
                    'videoId': video_id
                }
            }
        }
        
        response = requests.post(
            'https://www.googleapis.com/youtube/v3/playlistItems?part=snippet',
            headers=youtube_headers,
            json=request_body
        )
        return response.status_code == 200
    except Exception as e:
        print(f"Error adding video to playlist: {str(e)}")
        return False

def check_youtube_channel(youtube_headers):
    """Check if user has a YouTube channel"""
    try:
        response = requests.get(
            'https://www.googleapis.com/youtube/v3/channels?part=id&mine=true',
            headers=youtube_headers
        )
        return response.status_code == 200 and len(response.json().get('items', [])) > 0
    except Exception as e:
        print(f"Error checking YouTube channel: {str(e)}")
        return False

@connector_blueprint.route('/query_youtube', methods=['POST'])
def query_youtube():
    # First check if user is authenticated with YouTube
    if 'yt_access_token' not in session:
        print("No YouTube access token found - redirecting to YouTube login")
        # Store the Spotify playlist ID in session
        session['pending_playlist_id'] = request.form.get('playlist_id')
        return redirect('/youtube/login')
    
    # Get playlist_id either from form or from session
    playlist_id = request.form.get('playlist_id') or session.get('pending_playlist_id')
    if not playlist_id:
        print("No playlist ID found")
        return "No playlist selected", 400
    
    # Redirect to the playlist creation form
    return redirect('/youtube/create_playlist')

@connector_blueprint.route('/process_transfer')
def process_transfer():
    if 'yt_access_token' not in session:
        return redirect('/youtube/login')
        
    if 'pending_spotify_playlist_id' not in session:
        return "No playlist selected", 400
        
    # Get the stored Spotify playlist ID
    playlist_id = session.get('pending_spotify_playlist_id')
    
    # Rest of your existing playlist transfer code here...
    try:
        # Your existing code for creating playlist and transferring songs...
        pass
    except Exception as e:
        print(f"Error in process_transfer: {str(e)}")
        return f"An error occurred: {str(e)}", 500
    