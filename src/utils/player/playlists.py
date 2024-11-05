import os, re, src.lib.colors as cl
from src.utils.basics import normalize_text, getSoundName, get_sounds_from_playlist

def search_in_playlist(playlist, search_term):
    normalized_search = normalize_text(search_term)
    matching_sounds = []
    playlist_sounds = [os.path.join(playlist, sound) for sound in get_sounds_from_playlist(playlist)]
    for sound in playlist_sounds:
        if re.search(normalized_search, normalize_text(sound)): matching_sounds.append(sound)
    print(f"\nSounds found in {playlist.replace("\\", "/").rsplit("/", 1)[-1]}:")
    for i, sound in enumerate(matching_sounds):
        print(f"{cl.b}[{cl.w}{i+1}{cl.b}]{cl.w} {getSoundName(sound)}")
        # Add separator for visual clarity every 3 items.
        if (i + 1) % 3 == 0 and i != len(matching_sounds) - 1: print(f" {cl.w}|")