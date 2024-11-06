import time, threading, src.lib.globals as globals

def monitor_silence(next_sound_func):
    globals.is_first_sound = False
    def monitor():
        silent_seconds = 0
        while True:
            if globals.mixer is not None and globals.mixer.music.get_busy():
                sound_position = globals.mixer.music.get_pos() / 1000
                if sound_position % 1 == 0: silent_seconds += 1
                else: silent_seconds = 0
            else: silent_seconds = 0
            if silent_seconds >= 5:
                next_sound_func()
                silent_seconds = 0
            time.sleep(1)
    threading.Thread(target=monitor, daemon=True).start()

def fade_out(sound):
    for step in range(20):
        sound.set_volume(sound.get_volume() * (1 - step / 20))
        time.sleep(3/ 20)

def fade_in(sound, target_volume):
    for _ in range(20):
        sound.volume = min(target_volume, sound.volume + target_volume / 20)
        time.sleep(3 / 20)