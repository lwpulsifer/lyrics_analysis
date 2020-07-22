from get_lyrics import get_all_lyrics
from count_distinct_words import count_distinct, clean
import os
import json

def main():
    if os.path.exists("output.json"):
        with open("output.json", "r") as f:
            lyrics_dict = json.loads(f.read())
    else:
        lyrics_dict = get_all_lyrics()
    for artist in lyrics_dict:
        # print(f"Artist: {artist}")
        for album in lyrics_dict[artist]:
            total = 0
            count = 0
            # print(f"Album: {album}")
            for song in lyrics_dict[artist][album]:
                if "booklet" in song.lower() or "companion book" in song.lower():
                    break
                lyrics = clean(lyrics_dict[artist][album][song])
                distinct_words = count_distinct(lyrics)
                # print(f"Song {song} has {distinct_words} distinct words")
                count += 1
                total += distinct_words
            print(f"Album {album} has an average of {(total / count):.2f} distinct words per song")


if __name__ == "__main__":
    main()