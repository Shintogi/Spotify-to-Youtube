import os
from flask import Flask, render_template
from dotenv import load_dotenv
from spotify import spotify_blueprint

app = Flask(__name__)
app.secret_key = 'q8BX2vUR@IQNIrN6ajL9OkZLR3%y9rtaLsD'

load_dotenv()

app.register_blueprint(spotify_blueprint)
# app.register_blueprint(youtube_blueprint)

@app.route('/')
def welcome():
    return render_template('intropage.html')

@app.route('/playlists')
def playlists():
    return render_template('playlists.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)

    


