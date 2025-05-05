import src.lib.colors as cl
from mutagen.mp3 import MP3
from rich.panel import Panel
from collections import deque
from datetime import datetime
from rich.console import Console
from rich import print as rprint
from src.lib.config import config
from rich.markdown import Markdown
from mutagen.id3 import ID3, APIC, TIT2, TPE1
import os, re, sys, time, ctypes, asyncio, traceback, platform, subprocess, unicodedata

console = Console()

def cls() -> None:
    print(f"{cl.b}{cl.ENDC}", end="")
    if sys.platform == "win32": os.system("cls")
    else: os.system("clear")

def coloredText(word, hex_color) -> str:
    try:
        if not word.startswith("#"): word = f"#{str(word)}"
        rgb = tuple(int(hex_color.lstrip("#")[i:i+2], 16) for i in (0, 2, 4))
        return f"\033[38;2;{rgb[0]};{rgb[1]};{rgb[2]}m{str(word)}\033[0m"
    except: return word

"""
    Prompt the user for input with customizable formatting options.

    Args:
        prompt (str): The message displayed to the user as the input prompt.
        newline (bool, optional): Whether to add a newline before the prompt. Defaults to False.
        lowercase (bool, optional): Whether to convert the input to lowercase (only if format_type is str). Defaults to False.
        tab (bool, optional): Whether to add a tab before the prompt. Defaults to False.
        format_type (type, optional): The type to which the input should be converted. Defaults to str.

    Returns:
        The user's input converted to the specified format_type.

    Raises:
        ValueError: If the input cannot be converted to the specified format_type.
        EOFError: If there is an unexpected end of input.
"""
def quest(prompt, newline=False, lowercase=False, tab=False, format_type=str):    
    prefix = f"\n" if newline else ""
    prefix += f"\t" if tab else ""
    while True:
        try:
            response = input(f"{prefix}{cl.b}[{cl.w}?{cl.b}]{cl.w} {prompt}: ").strip()
            if format_type == int: value = int(response)
            elif format_type == str and lowercase: value = response.lower()
            else: value = response
            if config.general.clear_on_quest: 
                cls()
                time.sleep(0.25)
            return value
        except (ValueError, EOFError): terminal("e", "Enter a valid value.", timer=True)

def getPositive(q, default=True) -> bool:
    positive_responses = ["y", "yes", "yeah", "continue", "s", "si", "sí", "oui", "wa", "ja"]
    if default: positive_responses.append("")
    return q.lower() in positive_responses

def setColor(v):
    return f"{cl.g}True{cl.w}" if v == "True" or v == True else \
           f"{cl.r}False{cl.w}" if v == "False" or v == False else \
           f"{cl.r}{v}{cl.w}" if any(term in str(v).lower() for term in ["not", "error"]) else \
           f"{cl.y}{v}{cl.w}" if any(term in str(v).lower() for term in ["coming soon"]) else \
           f"{v}"

def terminal(typeMessage, string="", exitScript=False, clear="n", newline=True, timer=False) -> None:
    if (clear == "b" or typeMessage == "iom"): cls()
    if isinstance(typeMessage, str):
        if typeMessage == "e": 
            print(f"\n{cl.R} ERROR {cl.w} {string}") # X or ❌
            add_log_line(f"ERROR: {string}")
        if typeMessage == "s": print(f"\n{cl.g}✅ {string}{cl.w}") # ✓ or ✅
        if typeMessage == "i": rprint(f"{'\n' if newline else ''}[cyan]{string}[/cyan]")
        if typeMessage == "w": rprint(f"\n[bold yellow]Warning:[/bold yellow] [yellow]{string}[/yellow]")
        if typeMessage == "h": print(f"\n{cl.B}💡 TIP {cl.w} {string}") # X or ❌
        if typeMessage == "nmi": print(f"\n{cl.R} ERROR {cl.w} Could not install {string}. Please install it manually.")
        if typeMessage == "nei": print(f"\n{cl.R} ERROR {cl.w} {string} is not installed or not found in PATH. Please install it manually.")
        if typeMessage == "l": print("\nThis may take a few seconds...")
        if typeMessage == "info": console.print(Panel(Markdown(string), title="Sounder", title_align="left", expand=False, style="bold white"))
        if typeMessage == "iom": 
            print(f"\n{cl.R} ERROR {cl.w} Please enter a valid option.")
            time.sleep(2)
    elif isinstance(typeMessage, type) and issubclass(typeMessage, BaseException):
        if typeMessage == KeyboardInterrupt: print(f"\n{cl.R} ERROR {cl.w} Exiting Program: Canceled by user.")
        sys.exit(1)
    else: print(f"\nUnhandled typeMessage: {typeMessage}")
    if exitScript: sys.exit(1 if typeMessage == "e" else 0)
    if clear == "a" or typeMessage == "iom": cls()
    if timer: time.sleep(2)

def run_async(coroutine):
    return asyncio.get_event_loop().run_until_complete(coroutine)

def getSoundName(name) -> str:
    return name.replace("\\", "/").rsplit("/", 1)[-1].rsplit(".", 1)[0]

def get_sound_data(sound_path):
    response = {
        "duration": None, 
        "album_art_path": "./defaults/album_art_path.png",
        "artist": None,
        "sound_name": None
    }
    try:
        # Get sound duration.
        response["duration"] = int(MP3(sound_path).info.length)
        # Get artist and sound name.
        try:
            audio_id3 = ID3(sound_path)
            response["sound_name"] = audio_id3.get(TIT2, "unknown").text[0] if audio_id3.get(TIT2) else getSoundName(sound_path)
            response["artist"] = audio_id3.get(TPE1, "unknown").text[0] if audio_id3.get(TPE1) else "Enjoying the sound"
        except Exception as e:
            if config.general.developer_mode:
                terminal("e", f"Error extracting artist/sound name: {e}")
                traceback.print_exc()
            response["artist"] = "Unknown Artist"
            response["sound_name"] = getSoundName(sound_path)
        # Get album art.
        try:
            for frame in audio_id3.values():
                if isinstance(frame, APIC):
                    album_art_data = frame.data
                    break
            else: album_art_data = None
            if album_art_data:
                image_filename = f"temp/thumbnail/{response['sound_name']}.jpg"
                if os.path.isfile(image_filename): response["album_art_path"] = image_filename
                else: 
                    os.makedirs("temp/thumbnail", exist_ok=True)
                    with open(image_filename, "wb") as temp_file:
                        temp_file.write(album_art_data)
                    response["album_art_path"] = image_filename
        except Exception as e:
            if config.general.developer_mode:
                terminal("e", f"Error extracting album art: {e}")
                traceback.print_exc()
            response["album_art_path"] = "./defaults/album_art_path.png"
    except Exception as e:
        terminal("e", f"Error extracting sound data: {e}")
        if config.general.developer_mode: traceback.print_exc() # Print stack trace for debugging purposes.
    return response

def set_terminal_title(title: str):
    system = platform.system()
    title = title.strip()
    if title != "Sounder": title += " | Sounder"
    if system == "Windows": ctypes.windll.kernel32.SetConsoleTitleW(title)
    elif system in ["Linux", "Darwin"]: print(f"\033]0;{title}\007", end="", flush=True)
    else: raise OSError(f"Unsupported OS: {system}")

def normalize_text(text):
    return re.sub(r'[^a-z0-9\s]', "", unicodedata.normalize("NFD", text).encode("ascii", "ignore").decode("utf-8").lower())

# Function to get list of sounds from a playlist (directory).
def get_sounds_from_playlist(playlist):
    try: return [sound for sound in os.listdir(playlist) if sound.endswith(".mp3")]
    except FileNotFoundError:
        terminal("e", f"The path '{playlist}' was not found.")
        return []
    
def set_alias():
    system = platform.system()
    if system in ["Linux", "Darwin"]: subprocess.run([os.getenv("SHELL", "/bin/bash"), "-c", "alias Sounder='echo -n \"\"'"], check=True)
    elif system == "Windows": subprocess.run(["powershell", "-Command", 'function Sounder { "" | Out-Null }'], check=True)
    else: raise OSError(f"Unsupported OS: {system}")

log_lines = deque(maxlen=100)

def add_log_line(line: str):
    log_lines.append(f"[<span style='color:blue'>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</span>] {line}")

def show_log_markdown():
    cls()
    terminal("info", f"""### Last 100 lines of the log:\n\n{"\n".join(f"- {line}" for line in log_lines)}""", clear=True)