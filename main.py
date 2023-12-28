import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from bs4 import BeautifulSoup
import requests
import configparser
from albums import get_albums
import random
import re


#Todo: Handle lyrics that couldn't be loaded!!

config = configparser.ConfigParser()
config.read('config.ini')

cid = '807c9dda3d3746448321ae2d407faa78'
csecret = '0d910c898e074423920dc8231761da5c'

client_credentials_manager = SpotifyClientCredentials(client_id=cid, client_secret=csecret)
sp = spotipy.Spotify(client_credentials_manager = client_credentials_manager)


def scrape_lyrics(artistname, songname):
    artistname2 = str(artistname.replace(' ','-')) if ' ' in artistname else str(artistname)
    songname2 = str(songname.replace(' ','-')) if ' ' in songname else str(songname).lower()
    #print(songname2)
    #print(artistname2)
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
    songName = song['track']
    #print(songName)
    index_of_song = df1[df1['track'] == songName].index.tolist()
    
    # Stelle sicher, dass der Song im DataFrame vorhanden ist
    if index_of_song:
        index_of_song = index_of_song[0]
        test = scrape_lyrics(artist_name, songName)
        #print(test)
        
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

def removeBrackets(text):
    cleaned_text = re.sub(r'\[.*?\]', '', text)
    return cleaned_text

import re

import re

import re

import re

import re

def getChorus(lyrics):
    if lyrics is not None and isinstance(lyrics, str):
        pattern = re.compile(r'\[Chorus:?[^\]]*\](.*?)(?=\[.*?:|\Z)', re.IGNORECASE | re.DOTALL)
        match = pattern.search(lyrics)

        if match:
            return match.group(1).strip()

    return None






def printLyricsPart(song, difficulty):

    lyrics = song['lyrics']
    chorus = getChorus(lyrics)
    cleaned_lyrics = removeBrackets(lyrics)


    if difficulty.lower() == 'hard':
        words = re.findall(r'\b\w+\b', cleaned_lyrics)
        startpunkt = random.randint(0, len(words) - 40)

        auswahl = words[startpunkt:startpunkt + 40]

        print(' '.join(auswahl))

    elif difficulty.lower() == 'medium':
        words = re.findall(r'\b\w+\b', cleaned_lyrics)
        startpunkt = random.randint(0, len(words) - 80)

        auswahl = words[startpunkt:startpunkt + 80]

        print(' '.join(auswahl))

    elif difficulty.lower() == 'easy':
        if chorus:
            print(chorus)
        else:
            print(cleaned_lyrics)
    
    else:
        print(cleaned_lyrics)
       





def main():
    albums = get_albums()
    songs = get_album_tracks(albums)


    random_number = random.randint(0, 184)
    single_song = songs.iloc[random_number]
    #print(single_song)
    lyrics_onto_frame(songs, single_song, 'Kanye west')


    #update single song
    single_song = songs.iloc[random_number]

    #print(single_song)

    print("Enter the difficulty you want to play the game with")

    difficulty = input("Possibilitys are hard, medium and easy: ")

    printLyricsPart(single_song, difficulty)

    print("Enter your first guess")
    



if __name__ == "__main__":
    main()

#URI: spotify:playlist:10HzxiUA71aMAjGHcezh6p