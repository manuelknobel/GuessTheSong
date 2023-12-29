import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from bs4 import BeautifulSoup
import requests
import configparser
from albums import get_albums
import random
import re
import heapq


#To do List:
#  Abständbe bei lyrics, manchaml hat es keine Punkte und zwei Wörter sind zusammen
# Error Handling wenn die Lyrics nicht geholt werden können, dann einfach neuer song direkt

config = configparser.ConfigParser()
config.read('config.ini')

cid = config['DEFAULT']['cid']
csecret = config['DEFAULT']['csecret']

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
    
 
def printFullLyrics(song):
    lyrics = song['lyrics']
    cleaned_lyrics = removeBrackets(lyrics)
    print(cleaned_lyrics)

       
def seeRecord(guessRecord):
    if guessRecord == {}: 
        print("Spiele das Spiel erstmal, bevor du dir den Record anschaust")
        return
    else:
        smallesValues = heapq.nsmallest(3, guessRecord.items(), key=lambda x: x[1])
        print("Deine drei besten Songs!")
        for song, value in smallesValues:
            print(f"Song: {song}, Anzahl Versuche: {value}")



def main():
    albums = get_albums()
    songs = get_album_tracks(albums)
    global play_again
    play_again = 'yes'

    guess_record = {}

 
    
    def navigation():
        print("1: See Record: ")
        print("2: Play the game: ")
        print("3: Exit: ")

    def game():
        global play_again
        while play_again.lower() == 'yes':
            
            random_number = random.randint(0, 184)
            single_song = songs.iloc[random_number]
            #print(single_song)
            lyrics_onto_frame(songs, single_song, 'Kanye west')

            single_song = songs.iloc[random_number]

            print("Enter the difficulty you want to play the game with")

            difficulty = input("Possibilitys are hard, medium and easy: ")

            guess = None
            guessCount = 1

            while guess != single_song['track']:

                printLyricsPart(single_song, difficulty)

                guess = input("Enter your guess: ")

                if guess.lower() == single_song['track'].lower():
                    print(f"You won with {guessCount} needed guesses!")
                    guess_record[single_song['track']] = guessCount
                    break

                if guessCount >= 10:
                    endGame = input("You already needed 10 guesses, do you want to know the name of the song?")
                    if endGame.lower() == 'yes':
                        print("The song was")
                        print(single_song['track'])
                        guess_record[single_song] = guessCount
                        break
                    else:
                        continue
                else:
                    print("Wrong guess, try again")
                    guessCount += 1
                    difficulty = input("Enter the new difficulty, if you want to change it, enter stop if you want to stop and know the song Name: ")
                    if difficulty.lower() == 'stop':
                        print("The song was")
                        print(single_song['track'])
                        break

            print("Play again?")
            play_again = input("Yes or No:")

    print("Welcome to the Kanye West Guess the Song Game")
    print("You will be given a part of the lyrics and you have to guess the song")
    
    while True:
        print("----------------------------------------------")
        navigation()
        choice = input("Enter your choice: ")
        if choice == '1':
            seeRecord(guess_record)
        elif choice == '2':
            game()
        elif choice == '3':
            break
        else:
            print("Invalid Choice")
            continue

        
if __name__ == "__main__":
    main()

#URI: spotify:playlist:10HzxiUA71aMAjGHcezh6p