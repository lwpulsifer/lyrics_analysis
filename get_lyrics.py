import requests
from bs4 import BeautifulSoup
import json
import tqdm


def get_auth():
    import os
    dirlist = os.listdir()
    with open("authorization.txt", "r") as authfile:
        return authfile.read()


BASE_URL = 'https://api.genius.com'
HEADERS = {
    'Authorization': 'Bearer ' + get_auth()
}
ALBUMS_FILE = "albums.txt"


def remove_umlaut(string):
    """
    Removes umlauts from strings and replaces them with the letter+e convention
    :param string: string to remove umlauts from
    :return: unumlauted string
    """
    u = 'ü'.encode()
    U = 'Ü'.encode()
    a = 'ä'.encode()
    A = 'Ä'.encode()
    o = 'ö'.encode()
    O = 'Ö'.encode()
    ss = 'ß'.encode()

    string = string.encode()
    string = string.replace(u, b'u')
    string = string.replace(U, b'U')
    string = string.replace(a, b'a')
    string = string.replace(A, b'A')
    string = string.replace(o, b'o')
    string = string.replace(O, b'O')
    string = string.replace(ss, b'ss')

    string = string.decode('utf-8')
    return string


def get_clean_artist_name(artist_name):
    artist_name = "-".join(artist_name.split())
    return remove_umlaut(artist_name.title())


def get_clean_album_name(album_name):
    album_name = "-".join(album_name.split())
    return album_name.title()


def get_songs_from_album_artist(artist_name, album_name):
    c_artist_name = get_clean_artist_name(artist_name)
    c_album_name = get_clean_album_name(album_name)
    album_page = f"https://genius.com/albums/{c_artist_name}/{c_album_name}"
    page = requests.get(album_page)
    html = BeautifulSoup(page.text, 'html.parser')
    titles = html.find_all('h3', class_='chart_row-content-title')

    def basic_clean(title):
        '''Specific to this form of html element from genius artist pages'''
        return title.get_text().replace("\n", " ").replace("Lyrics", "").strip()

    return [basic_clean(title) for title in titles]


def request_song_info(song_title, artist_name):
    search_url = BASE_URL + '/search'
    data = {'q': song_title + ' ' + artist_name}
    response = requests.get(search_url, data=data, headers=HEADERS)

    return response


def scrape_song_url(url):
    page = requests.get(url)
    html = BeautifulSoup(page.text, 'html.parser')
    lyrics = html.find('div', class_='lyrics').get_text()

    return lyrics


def get_lyrics(song_title, artist_name):

    response = request_song_info(song_title, artist_name)
    json_data = response.json()
    remote_song_info = None
    # with open("test.json", "a") as write_file:
    #     json.dump(json_data, write_file)

    for hit in json_data['response']['hits']:
        # print(hit['result'])
        potential_artist_name = hit['result']['primary_artist']['name']
        if artist_name.lower() in potential_artist_name.lower():
            remote_song_info = hit
            break

    # Extract lyrics from URL if the song was found
    song_url = None
    if remote_song_info:
        song_url = remote_song_info['result']['url']
    
    if song_url:
        return scrape_song_url(song_url)
    else:
        print(f"\nLyrics not found for song {song_title} by {artist_name}\n")
        return "Not found"


def get_albums(albums_file=ALBUMS_FILE):
    with open(albums_file, 'r') as albums_file:
        albums = albums_file.readlines()
        clean_albums = [tuple(line.rstrip("\n").split(",")) for line in albums]
        print("Getting albums:\n" + str(clean_albums))
    return clean_albums


def get_all_lyrics(albums_file=ALBUMS_FILE, outfile="output.json"):
    lyrics_dict = {}
    for artist, album in get_albums(albums_file):
        if artist not in lyrics_dict:
            lyrics_dict[artist] = {}
        lyrics_dict[artist][album] = {}
        print(f"Getting lyrics for album {album} by {artist}")
        for song in tqdm.tqdm(get_songs_from_album_artist(artist, album)):
            lyrics_dict[artist][album][song] = get_lyrics(song, artist)
    with open(outfile, 'w') as output:
        json.dump(lyrics_dict, output)
    return lyrics_dict


if __name__ == "__main__":
    get_all_lyrics()
