from pygame import mixer
from mutagen.mp3 import MP3
import src.lib.colors as cl
import src.lib.data as data
from dotenv import load_dotenv
from src.lib.config import config
from src.integrations.macros import start_macros
from src.integrations.worker import update_all_presences
from src.utils.basics import cls, quest, terminal, getSoundName, set_terminal_title
import os, sys, time, random, signal, src.lib.globals as globals, pygame, pyfiglet, warnings, platform, threading

# Initialize playlists list.
playlists = []
# Custom event for sound end.
SOUND_END_EVENT = pygame.USEREVENT + 1
# State variables.
current_sound_index = 0
previous_sound_index = 0
paused_position = 0.0
is_shuffled = False
volume = 1.0 # Default maximum volume.
clock = pygame.time.Clock()

# Function to get list of playlists (directories) or sounds (files).
def get_playlists_or_sounds():
    return [name for name in os.listdir(config.general.sounds_folder_path) if os.path.isdir(os.path.join(config.general.sounds_folder_path, name)) and name != "Playlist Name"]

# Function to get list of sounds from a playlist (directory).
def get_sounds_from_playlist(playlist):
    try: return [sound for sound in os.listdir(playlist) if sound.endswith(".mp3")]
    except FileNotFoundError:
        print(f"Error: The path '{playlist}' was not found.")
        return []

# Function to list playlists and choose one.
def list_playlists():
    # Lists available playlists and allows the user to select one.
    global playlists
    playlists = get_playlists_or_sounds() # Populate the playlists list.
    print("Available Playlists:")
    for i, playlist in enumerate(playlists):
        print(f"{cl.b}[{cl.w}{i+1}{cl.b}]{cl.w} {playlist}")
        # Add separator for visual clarity every 3 items.
        if (i + 1) % 3 == 0 and i != len(playlists) - 1: print(f" {cl.w}|")
    print(f" {cl.w}|")

# Function to list sounds in a playlist and select one.
def list_sounds(playlist, sound_choice=None):
    global current_sound_index
    globals.current_sounds = [os.path.join(playlist, sound) for sound in get_sounds_from_playlist(playlist)]
    print(f"\nSounds in {playlist.replace("\\", "/").rsplit("/", 1)[-1]}:")
    for i, sound in enumerate(globals.current_sounds):
        print(f"{cl.b}[{cl.w}{i+1}{cl.b}]{cl.w} {getSoundName(sound)}")
        # Add separator for visual clarity every 3 items.
        if (i + 1) % 3 == 0 and i != len(globals.current_sounds) - 1: print(f" {cl.w}|")
    print(f" {cl.w}|")
    while True:
        if not sound_choice: sound_choice = quest("Enter the number of the sound to play, or press Enter to skip selection", lowercase=True)
        if sound_choice.isdigit():
            sound_index = int(sound_choice) - 1
            if 0 <= sound_index < len(globals.current_sounds): return globals.current_sounds, sound_index
            else: terminal("e", "Invalid sound selection. Please choose a number within the range.")
        elif sound_choice == "": return globals.current_sounds, 0
        else: terminal("e", "Invalid input. Please enter a number or press Enter to skip.")
        sound_choice = None

def play_selected_sound(sound_index, on_error_list=False):
    global current_sound_index
    if sound_index is not None: current_sound_index = sound_index
    play_sound(on_error_list=on_error_list)

def select_playlist():
    global playlists
    while True:
        list_playlists()
        playlist_choice = quest("Enter the number of the playlist to select, 'a' to play all sounds randomly", lowercase=True)
        if playlist_choice == "a": playlists = ["all"]; break
        else:
            try: playlists = [os.path.join(config.general.sounds_folder_path, playlists[int(playlist_choice) - 1])]; break
            except (IndexError, ValueError): terminal("e", "Invalid selection. Please try again.")

def load_sounds():
    # Loads sounds from selected playlists.
    globals.current_sounds = []
    for playlist in playlists:
        if playlist == "all":
            for dirpath, _, filenames in os.walk(config.general.sounds_folder_path):
                globals.current_sounds.extend([os.path.join(dirpath, sound) for sound in filenames if sound.endswith(".mp3")])
        else: globals.current_sounds.extend([os.path.join(playlist, sound) for sound in get_sounds_from_playlist(playlist)])
    if not globals.current_sounds: return terminal("e", "No sounds found in the selected playlists.", exitScript=True)
    random.shuffle(globals.current_sounds) # Shuffle sounds for random playback.

def play_sound(restart=False, on_error_list=False):
    global paused_position, previous_sound_index
    # Plays the current sound.
    if globals.current_sounds:
        try:
            sound_path = globals.current_sounds[current_sound_index]
            mixer.music.load(sound_path)
            mixer.music.set_volume(volume)
            if restart or paused_position == 0.0 or previous_sound_index != current_sound_index:
                mixer.music.play()
                paused_position = 0.0 # Reset paused position if restarting.
            else: mixer.music.play(start=paused_position)
            mixer.music.set_endevent(SOUND_END_EVENT) # Set the end event for sound completion.
            globals.is_playing = True
            globals.stop_requested = False
            # Get sound duration in minutes and seconds.
            audio = MP3(sound_path)
            duration_minutes = int(audio.info.length // 60)
            duration_seconds = int(audio.info.length % 60)
            sound_name = getSoundName(os.path.basename(sound_path))
            print(f"{cl.BOLD}⏯️ Currently Playing:{cl.ENDC} {sound_name} {cl.g}[{duration_minutes}:{duration_seconds:02d} min]{cl.ENDC}")
            set_terminal_title(f"{sound_name} | Sounder")
            update_all_presences(True, sound_name=sound_name, sound_path=globals.current_sounds[current_sound_index])
        except pygame.error as e: terminal("e", f"Error loading or playing sound: {e}")
        except Exception as e: 
            terminal("e", f"Error playing sound: {e}")
            if on_error_list: play_selected_sound(sound_index) if (sound_index := list_sounds(playlists[0])[1]) is not None else None
    else: terminal("e", "No sounds to play.")

def stop_sound():
    global paused_position
    # Stops the current sound.
    try:
        paused_position = mixer.music.get_pos() / 1000.0
        mixer.music.pause()
        globals.is_playing = False
        globals.stop_requested = True
        update_all_presences(False)
        print(f"{cl.BOLD}⏸️ Sound stopped.{cl.ENDC}")
    except Exception as e: terminal("e", f"Error stopping.")

def restart_sound():
    # Restarts the current sound from the beginning.
    stop_sound()
    play_sound(restart=True)
    print(f"{cl.BOLD}🔄 Sound restarted.{cl.ENDC}")

def next_sound():
    # Plays the next sound in the list, or a random one if shuffle is enabled.
    global current_sound_index, previous_sound_index
    previous_sound_index = current_sound_index
    if is_shuffled: current_sound_index = random.choice([i for i in range(len(globals.current_sounds)) if i != previous_sound_index])
    else: current_sound_index = (current_sound_index + 1) % len(globals.current_sounds)
    play_sound()

def prev_sound():
    # Plays the previous sound in the list.
    global current_sound_index
    current_sound_index = (current_sound_index - 1) % len(globals.current_sounds)
    play_sound()

def adjust_volume(amount):
    # Adjusts the volume by a given amount (positive or negative).
    global volume
    volume = max(0.0, min(1.0, volume + amount)) # Ensure volume stays between 0.0 and 1.0.
    mixer.music.set_volume(volume)
    volume_percentage = int(volume * 100)
    print(f"{cl.BOLD}{'🔇' if volume_percentage == 0 else '🔊'} Volume:{cl.ENDC} {volume_percentage}%")

def toggle_shuffle():
    # Toggles between shuffle mode and sequential mode.
    global is_shuffled
    is_shuffled = not is_shuffled
    print(f"{cl.BOLD}🔀 Playback mode:{cl.ENDC} {'Shuffle' if is_shuffled else 'Sequential'}")

def handle_event(event):
    # Handles pygame events.
    if event.type == SOUND_END_EVENT and not globals.stop_requested: next_sound() # Play the next sound if stop was not requested.

def user_input_thread():
    global running
    while running:
        print("\nCommands: [p] Play Sound, [n] Next Sound, [v] Previous Sound, [v+] Increase Volume, [v-] Decrease Volume, [s] Toggle Shuffle, [l] List Sounds, [b] Back to Playlist Selection, [r] Restart Sound, [x] Stop Sound, [q] Quit")
        command = quest("Enter command", lowercase=True)
        if command == "p": play_sound()
        elif command == "n": next_sound()
        elif command == "v": prev_sound()
        elif command == "v+": adjust_volume(0.1)
        elif command == "v-": adjust_volume(-0.1)
        elif command == "s": toggle_shuffle()
        elif command == "l": play_selected_sound(sound_index) if (sound_index := list_sounds(playlists[0])[1]) is not None else None
        elif command == "b":
            select_playlist()
            if "all" not in playlists:
                load_sounds()
                play_sound()
        elif command == "x": stop_sound()
        elif command == "r": restart_sound()
        elif command == "q":
            if config.general.quick_exit: os._exit(0)
            else: stop_sound()
            running = False
            break
        # elif command.isdigit() and getPositive(quest(f"That's not a valid command, maybe you want to choose a sound from the current playlist? {cl.g}[y]{cl.ENDC}/n")):
        #     command = int(command) 
        #     play_selected_sound(command - 1, on_error_list=True) if (command > 1 and command < len(playlists[0][1])) is not None else None
        else: terminal("e", "Enter valid command.")
        time.sleep(0.1) # Small delay to prevent high CPU usage.

def signal_handler(sig, frame):
    global running
    if config.general.quick_exit: os._exit(0)
    else:
        running = False
        stop_sound()
        update_all_presences(False)
        pygame.quit()
        sys.exit(0)

if __name__ == "__main__":
    # Production only.
    if not config.general.developer_mode: warnings.filterwarnings("ignore", category=RuntimeWarning)
    # Banner
    cls()
    print(pyfiglet.figlet_format("SOUNDER"))
    print(f'\n{cl.des_space}{cl.b}>> {cl.w}Welcome to Sounder, remember to use it responsibly. \n{cl.des_space}{cl.b}>> {cl.w}Join to our Discord server on tpe.li/dsc\n{cl.des_space}{cl.b}>> {cl.w}Version: {data.version}\n')
    if not sys.version[0] in "3": terminal("e", "Sounder only works properly with Pytnon 3. Please upgrade/use Python 3.", exitScript=True)
    current_os = platform.system()
    if current_os not in ["Linux", "Darwin", "Windows"]: terminal("e", f"Sounder macros only support Linux, macOS, and Windows. Your OS ({current_os}) is not supported.", exitScript=True)
    load_dotenv(override=True)

    # Handle Ctrl+C to exit quickly and cleanly.
    signal.signal(signal.SIGINT, signal_handler)

    # Initialize pygame and the sound mixer.
    pygame.init()
    mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
    select_playlist()
    if "all" not in playlists:
        load_sounds()
        play_sound()
    running = True
    globals.stop_requested = False
    input_thread = threading.Thread(target=user_input_thread)
    input_thread.start()
    start_macros()
    try:
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: running = False
                handle_event(event)
            # Check if the music has stopped playing.
            if not mixer.music.get_busy() and globals.is_playing and not globals.stop_requested: next_sound()
            clock.tick(30) # Limit the loop to 30 FPS.
    except (KeyboardInterrupt, EOFError):
        terminal("e", "Interrupted by user.")
        if config.general.quick_exit: os._exit(0)
        else: update_all_presences(False)
    finally:
        if config.general.quick_exit: os._exit(0)
        else:
            stop_sound()
            update_all_presences(False)
            input_thread.join()
            pygame.quit()