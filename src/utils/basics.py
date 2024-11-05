import src.lib.colors as cl
from mutagen.mp3 import MP3
from rich.panel import Panel
from rich.console import Console
from rich import print as rprint
from src.lib.config import config
from rich.markdown import Markdown
from mutagen.id3 import ID3, APIC, TIT2, TPE1
import os, sys, time, ctypes, asyncio, traceback, platform

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
        if typeMessage == "e": print(f"\n{cl.R} ERROR {cl.w} {string}") # X or ❌
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
    if system == "Windows": ctypes.windll.kernel32.SetConsoleTitleW(title)
    elif system in ["Linux", "Darwin"]: print(f"\033]0;{title}\007", end="", flush=True)
    else: raise OSError(f"Unsupported OS: {system}")