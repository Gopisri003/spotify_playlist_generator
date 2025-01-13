import spotipy
from spotipy.oauth2 import SpotifyOAuth
from bs4 import BeautifulSoup
import requests
from pprint import pprint
import os
from dotenv import load_dotenv
load_dotenv(".env")

# ----------------------Getting authentication-----------------------------
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
SPOTIFY_URI = os.getenv("SPOTIFY_URI")
USERNAME = os.getenv("SPOTIFY_USERNAME")

scope = "playlist-modify-private"
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope,
                                               client_id=CLIENT_ID,
                                               client_secret=CLIENT_SECRET,
                                               redirect_uri=SPOTIFY_URI,
                                               cache_path="token.txt",
                                               show_dialog=True,
                                               username=USERNAME))
user_id = sp.current_user()["id"]


# -----------------------Scraping from billboard--------------------------------
user_input = input("What year do you want to travel to . Type date in this format YYYY-MM-DD:")
response = requests.get(url=f"https://www.billboard.com/charts/hot-100/{user_input}/",
                        headers={
                            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                                          "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                            "Accept-Language": "en-US,en;q=0.9",
                            "Accept-Encoding": "gzip, deflate, br",
                            "Connection": "keep-alive",
                        }
                        )
response.raise_for_status()
html_text = response.text
soup = BeautifulSoup(html_text, "html.parser")
top_song = soup.find(name="h3", id="title-of-a-story", class_="c-title a-no-trucate a-font-primary-bold-s u-letter-"
                                                              "spacing-0021 u-font-size-23@tablet lrv-u-font-size-16 u-"
                                                              "line-height-125 u-line-height-normal@mobile-max a-"
                                                              "truncate-ellipsis u-max-width-245 "
                                                              "u-max-width-230@tablet-"
                                                              "only u-letter-spacing-0028@tablet")
songs = [top_song.getText().strip()]

other_top_songs = soup.find_all(name="h3", id="title-of-a-story", class_="c-title a-no-trucate a-font-primary-bold-s "
                                                                         "u-letter-spacing-0021 "
                                                                         "lrv-u-font-size-18@tablet "
                                                                         "lrv-u-font-size-16 u-line-height-125 "
                                                                         "u-line-height-normal@mobile-max "
                                                                         "a-truncate-ellipsis u-max-width-330 "
                                                                         "u-max-width-230@tablet-only")

for music in other_top_songs:
    songs.append(music.getText().strip())

# ------------------------Getting song Url--------------------------------------
song_titles = [song.getText().strip() for song in soup.select("li ul li h3")]
song_artist = [artist.getText().strip() for ind, artist in enumerate(soup.select("li ul li span")) if ind % 7 == 0]

song_dict = dict(zip(song_artist, song_titles))
track_ids = []
for song in song_dict:
    track = sp.search(q=f"artist: {song} track: {song_dict[song]}", type="track", market="US")
    try:
        track_id = track["tracks"]["items"][0]["uri"]
        track_ids.append(track_id)
    except IndexError:
        print(f"{song_dict[song]} does not exist")

# ------------------------Creating a new private playlist in Spotify----------------------------------
playlist = sp.user_playlist_create(user=user_id, name=f"{user_input} Billboard 100", public=False)
print(playlist)

# -----------------------Adding songs found into the new playlist---------------------------------------
sp.playlist_add_items(playlist_id=playlist["id"], items=track_ids)


