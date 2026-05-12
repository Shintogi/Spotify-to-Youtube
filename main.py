import os
from dotenv import load_dotenv
from requests import Session 
load_dotenv() #runs the env before the blueprints to prevent running into client id invalid error
from flask import Flask, render_template
from spotify import spotify_blueprint
from youtube import youtube_blueprint
from connector import connector_blueprint
from flask_session import Session
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')
app.config['SESSION_TYPE'] = 'filesystem'  # stores session data in server files instead of browser cookie
app.config['SESSION_FILE_DIR'] = './flask_session'  # folder where session files are saved
app.config['SESSION_PERMANENT'] = False  # session expires when browser closes
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # allows browser to send session cookie back after external redirects (e.g. Google OAuth)
app.config['SESSION_COOKIE_SECURE'] = False  # allows session cookie over plain http (required for localhost dev)
app.config['SESSION_COOKIE_NAME'] = 'spotify_youtube_session'
Session(app)

app.register_blueprint(spotify_blueprint, url_prefix='/spotify')
app.register_blueprint(youtube_blueprint, url_prefix='/youtube')
app.register_blueprint(connector_blueprint, url_prefix='/connector')

@app.route('/')
def welcome():
    return render_template('intropage.html')

@app.route('/playlists')
def playlists():
    return render_template('playlists.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)




