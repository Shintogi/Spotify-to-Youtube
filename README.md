# Spotify to Youtube
 Transfering spotify songs to youtube

### Setup
1. Clone the repo
   ```
   bash git clone https://github.com/shintogi/spot-to-tube.git
   ```
2. Cd into the project directory
 ```
 bash
cd spot-to-tube
 ```
3.Install required packages  
   ```
 bash
 pip install -r requirements.txt
 ```
 optional 
 ```
 Flask==2.0.3
 requests==2.26.0
 python-dotenv==0.19.2
 ```
4. Set up your environment variables in a `.env` file  
   ```plaintext
   SPOTIPY_CLIENT_ID=your_spotify_client_id
   SPOTIPY_CLIENT_SECRET=your_spotify_client_secret
   YOUTUBE_CLIENT_ID=your_youtube_client_id
   YOUTUBE_CLIENT_SECRET=your_youtube_client_secret
   ```
5. Run the application  
   ```bash
   python main.py

   ## Usage

1. Visit the welcome page at `http://localhost:5000/`.
2. Click on "Login with Spotify" to authenticate your Spotify account.
3. After logging in, you will be redirected to view your Spotify playlists.
4. Select a playlist and click "Query YouTube" to start the transfer process.
5. Follow the prompts to log in to your YouTube account and create a new playlist.
##  Contact
Denzel Fynn - denzelfynn100@gmail.com
## Roadmap
- Add support for transferring individual tracks.
- Implement user settings for managing API keys.
- Enhance error handling and user feedback.
