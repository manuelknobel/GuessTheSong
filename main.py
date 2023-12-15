import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from bs4 import BeautifulSoup
import requests
import configparser
from albums import get_albums
import random

config = configparser.ConfigParser()
config.read('config.ini')

cid = config['DEFAULT']['cid']
csecret = config['DEFAULT']['csecret']

client_credentials_manager = SpotifyClientCredentials(client_id=cid, client_secret=csecret)
sp = spotipy.Spotify(client_credentials_manager = client_credentials_manager)


def scrape_lyrics(artistname, songname):
    artistname2 = str(artistname.replace(' ','-')) if ' ' in artistname else str(artistname)
    songname2 = str(songname.replace(' ','-')) if ' ' in songname else str(songname).lower()
    print(songname2)
    print(artistname2)
    page = requests.get('https://genius.com/'+ artistname2 + '-' + songname2 + '-' + 'lyrics')
    html = BeautifulSoup(page.text, 'html.parser')
    lyrics1 = html.find_all("div", class_="lyrics")
    lyrics2 = html.find_all("div", class_="Lyrics__Container-sc-1ynbvzw-1 kUgSbL")

    lyrics = None
    if lyrics1:
        lyrics_elements = [element.get_text() for element in lyrics1]
        lyrics = '\n'.join(lyrics_elements)
    elif lyrics2:
        lyrics_elements = [element.get_text() for element in lyrics2]
        lyrics = '\n'.join(lyrics_elements)

    elif lyrics1 == lyrics2 == None:
        lyrics = None
    return lyrics

def lyrics_onto_frame(df1, song, artist_name):
    # Finde den Index des Songs im DataFrame
    index_of_song = df1[df1['track'] == song].index.tolist()
    
    # Stelle sicher, dass der Song im DataFrame vorhanden ist
    if index_of_song:
        index_of_song = index_of_song[0]
        test = scrape_lyrics(artist_name, song)
        print(test)
        
        # Füge die Lyrics nur für den bestimmten Song hinzu
        df1.loc[index_of_song, 'lyrics'] = test
        
    


def get_album_tracks(albums):
    uri = []
    track = []
    duration = []
    explicit = []
    track_number = []
    
    for album_key, album_value in albums.items():
        one = sp.album_tracks(album_value, limit=50, offset=0, market='US')
        df1 = pd.DataFrame(one)
        
        for i, x in df1['items'].items():
            uri.append(x['uri'])
            track.append(x['name'])
            duration.append(x['duration_ms'])
            explicit.append(x['explicit'])
            track_number.append(x['track_number'])
        
    df2 = pd.DataFrame({
    'uri':uri,
    'track':track,
    'duration_ms':duration,
    'explicit':explicit,
    'track_number':track_number})
    
    return df2


def main():
    albums = get_albums()
    songs = get_album_tracks(albums)


    random_number = random.randint(0, 184)
    single_song = songs.iloc[random_number, 1]
    print(single_song)
    songs_with_lyrics = lyrics_onto_frame(songs, single_song, 'Kanye west')


    print(songs.iloc[random_number])



if __name__ == "__main__":
    main()

#URI: spotify:playlist:10HzxiUA71aMAjGHcezh6p