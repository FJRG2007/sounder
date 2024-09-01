from pygame import mixer
import src.lib.colors as cl
import src.lib.data as data
from dotenv import load_dotenv
from src.integrations.worker import update_all_presences
import os, sys, time, random, pygame, pyfiglet, threading
from src.utils.basics import cls, quest, terminal, getSoundName

# Path to the root folder containing playlists.
root_folder = "./sounds"
# Initialize playlists list.
playlists = []

# Custom event for song end.
SONG_END_EVENT = pygame.USEREVENT + 1

# Function to get list of playlists (directories) or songs (files).
def get_playlists_or_songs():
    return [name for name in os.listdir(root_folder) if os.path.isdir(os.path.join(root_folder, name)) and name != "Playlist Name"]

# Function to get list of songs from a playlist (directory).
def get_songs_from_playlist(playlist):
    try: return [song for song in os.listdir(playlist) if song.endswith(".mp3")]
    except FileNotFoundError:
        print(f"Error: The path '{playlist}' was not found.")
        return []

# Function to list playlists and choose one.
def list_playlists():
    # Lists available playlists and allows the user to select one.
    global playlists
    playlists = get_playlists_or_songs()  # Populate the playlists list.
    print("Available Playlists:")
    for i, playlist in enumerate(playlists):
        print(f"{cl.b}[{cl.w}{i+1}{cl.b}]{cl.w} {playlist}")
        # Add separator for visual clarity every 3 items.
        if (i + 1) % 3 == 0 and i != len(playlists) - 1: print(f" {cl.w}|")
    print(f" {cl.w}|")

# Function to list songs in a playlist and select one.
def list_songs(playlist):
    # Lists all songs in the given playlist and allows the user to select one.
    global current_songs, current_song_index
    current_songs = [os.path.join(playlist, song) for song in get_songs_from_playlist(playlist)]
    print(f"\nSongs in {playlist.replace("\\", "/").rsplit("/", 1)[-1]}:")
    for i, song in enumerate(current_songs):
        print(f"{cl.b}[{cl.w}{i+1}{cl.b}]{cl.w} {getSoundName(song)}")
        # Add separator for visual clarity every 3 items.
        if (i + 1) % 3 == 0 and i != len(current_songs) - 1: print(f" {cl.w}|")
    # Prompt user to select a song.
    song_choice = quest("Enter the number of the song to play, or press Enter to skip selection", lowercase=True)
    
    # Check if a song number was chosen.
    if song_choice.isdigit():
        song_index = int(song_choice) - 1
        if 0 <= song_index < len(current_songs): return current_songs, song_index  # Return the list of songs and the chosen index.
        else:
            print("Invalid song selection. Playing the first song.")
            return current_songs, 0
    else: return current_songs, 0  # Default to the first song if no selection is made.

def play_selected_song(song_index):
    global current_song_index
    if song_index is not None: current_song_index = song_index
    play_song()

# Function to handle playlist selection.
def select_playlist():
    # Allows the user to select a playlist.
    global playlists  # Declare playlists as global.
    list_playlists()
    playlist_choice = quest("Enter the number of the playlist to select, 'a' to play all songs randomly", lowercase=True)
    if playlist_choice == "a": playlists = ["all"]
    else:
        try: playlists = [os.path.join(root_folder, playlists[int(playlist_choice) - 1])]
        except (IndexError, ValueError):
            print("Invalid selection.")
            exit()

# State variables.
current_song_index = 0
is_shuffled = False
volume = 1.0 # Default maximum volume.
current_songs = []
is_playing = False # To track if a song is currently playing.
stop_requested = False  # To track if stop has been requested.

def load_songs():
    # Loads songs from selected playlists.
    global current_songs
    current_songs = []
    for playlist in playlists:
        if playlist == "all":
            for dirpath, _, filenames in os.walk(root_folder):
                current_songs.extend([os.path.join(dirpath, song) for song in filenames if song.endswith(".mp3")])
        else: current_songs.extend([os.path.join(playlist, song) for song in get_songs_from_playlist(playlist)])
    if not current_songs:
        print("No songs found in the selected playlists.")
        exit()
    random.shuffle(current_songs) # Shuffle songs for random playback.

def play_song():
    # Plays the current song.
    global is_playing, stop_requested
    if current_songs:
        try:
            mixer.music.load(current_songs[current_song_index])
            mixer.music.set_volume(volume)
            mixer.music.play()
            mixer.music.set_endevent(SONG_END_EVENT) # Set the end event for song completion.
            is_playing = True
            stop_requested = False
            song_name = getSoundName(os.path.basename(current_songs[current_song_index]))
            print(f"{cl.BOLD}⏯️ Currently Playing:{cl.ENDC} {song_name}")
            update_all_presences(True, sound_name=song_name, sound_path=current_songs[current_song_index])
        except pygame.error as e: terminal("e", f"Error loading or playing song: {e}")
        except Exception as e: terminal("e", f"Error playing song: {e}")
    else: print("No songs to play.")

def stop_song():
    # Stops the current song.
    global is_playing, stop_requested
    if is_playing:
        mixer.music.stop()
        is_playing = False
        stop_requested = True
        update_all_presences(False)
        print("Song stopped.")

def restart_song():
    # Restarts the current song from the beginning.
    stop_song()
    play_song()
    print("Song restarted.")

def next_song():
    # Plays the next song in the list, or a random one if shuffle is enabled.
    global current_song_index
    if is_shuffled: current_song_index = random.randint(0, len(current_songs) - 1)
    else: current_song_index = (current_song_index + 1) % len(current_songs)
    play_song()

def prev_song():
    # Plays the previous song in the list.
    global current_song_index
    current_song_index = (current_song_index - 1) % len(current_songs)
    play_song()

def adjust_volume(amount):
    # Adjusts the volume by a given amount (positive or negative).
    global volume
    volume = max(0.0, min(1.0, volume + amount))  # Ensure volume stays between 0.0 and 1.0.
    mixer.music.set_volume(volume)
    print(f"Volume: {int(volume * 100)}%")

def toggle_shuffle():
    # Toggles between shuffle mode and sequential mode.
    global is_shuffled
    is_shuffled = not is_shuffled
    print(f"Playback mode: {'Shuffle' if is_shuffled else 'Sequential'}")

def handle_event(event):
    # Handles pygame events.
    if event.type == SONG_END_EVENT and not stop_requested: next_song()  # Play the next song if stop was not requested.

clock = pygame.time.Clock()

def user_input_thread():
    global running
    while running:
        print("\nCommands: [p] Play Song, [n] Next Song, [v] Previous Song, [v+] Increase Volume, [v-] Decrease Volume, [s] Toggle Shuffle, [l] List Songs, [b] Back to Playlist Selection, [r] Restart Song, [x] Stop Song, [q] Quit")
        command = quest("Enter command", lowercase=True)
        if command == "p": play_song()
        elif command == "n": next_song()
        elif command == "v": prev_song()
        elif command == "v+": adjust_volume(0.1)
        elif command == "v-": adjust_volume(-0.1)
        elif command == "s": toggle_shuffle()
        elif command == "l": play_selected_song(song_index) if (song_index := list_songs(playlists[0])[1]) is not None else None
        elif command == "b":
            select_playlist()
            if "all" not in playlists:
                load_songs()
                play_song()
        elif command == "x": stop_song()
        elif command == "r": restart_song()
        elif command == "q":
            stop_song()
            running = False
        time.sleep(0.1)  # Small delay to prevent high CPU usage.

if __name__ == "__main__":
    # Banner
    cls()
    print(pyfiglet.figlet_format("SOUNDER"))
    print(f'\n{cl.des_space}{cl.b}>> {cl.w}Welcome to Sounder, remember to use it responsibly. \n{cl.des_space}{cl.b}>> {cl.w}Join to our Discord server on tpe.li/dsc\n{cl.des_space}{cl.b}>> {cl.w}Version: {data.version}\n')
    if not sys.version[0] in "3":
        terminal("e", "Sounder only works properly with Pytnon 3. Please upgrade/use Python 3.", exitScript=True)
        exit(1)
    load_dotenv(override=True)
    # Initialize pygame and the sound mixer.
    pygame.init()
    mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
    select_playlist()
    if "all" not in playlists:
        load_songs()
        play_song()

    running = True
    stop_requested = False
    input_thread = threading.Thread(target=user_input_thread)
    input_thread.start()

    try:
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: running = False
                handle_event(event)

            # Check if the music has stopped playing.
            if not mixer.music.get_busy() and is_playing and not stop_requested:
                print("Music stopped, playing next song") # Debug print.
                next_song()
            clock.tick(30)  # Limit the loop to 30 FPS.
    except KeyboardInterrupt:
        terminal("e", "Interrupted by user.")
        update_all_presences(False)
    finally:
        stop_song()
        update_all_presences(False)
        pygame.quit()
        input_thread.join()