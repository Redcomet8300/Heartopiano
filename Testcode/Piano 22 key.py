import os
import json
import time
import argparse
from mido import MidiFile
import keyboard

# ==============================
# STATE
# ==============================
play_state = "idle"
OCT = 12

# ==============================
# NOTE NAMES
# ==============================
NOTE_NAMES = ['C','C#','D','D#','E','F','F#','G','G#','A','A#','B']

# ==============================
# KEY MAP (EXACT AS PROVIDED)
# ==============================

LOW = {
    'C': ',',   'C#': 'l',
    'D': '.',   'D#': ';',
    'E': '/',
    'F': 'o',   'F#': '0',
    'G': 'p',   'G#': '-',
    'A': '[',   'A#': '=',
    'B': ']'
}

MID = {
    'C': 'z',   'C#': 's',
    'D': 'x',   'D#': 'd',
    'E': 'c',
    'F': 'v',   'F#': 'g',
    'G': 'b',   'G#': 'h',
    'A': 'n',   'A#': 'j',
    'B': 'm'
}

HIGH = {
    'C': 'q',   'C#': '2',
    'D': 'w',   'D#': '3',
    'E': 'e',
    'F': 'r',   'F#': '5',
    'G': 't',   'G#': '6',
    'A': 'y',   'A#': '7',
    'B': 'u',
    'C6': 'i'   # special case
}

# ==============================
# MIDI FILTER
# ==============================
def midi_playable(msg):
    return (
        not msg.is_meta
        and msg.type == 'note_on'
        and msg.velocity > 0
    )

# ==============================
# NOTE → KEY (NO OCTAVE LIMIT)
# ==============================
def pitch_to_key(pitch):
    note = NOTE_NAMES[pitch % 12]
    octave = pitch // 12 - 1

    # C6
    if note == 'C' and octave >= 6:
        return 'i', 84

    if octave <= 3:
        return LOW.get(note), 48 + (pitch % 12)

    if octave == 4:
        return MID.get(note), 60 + (pitch % 12)

    if octave >= 5:
        return HIGH.get(note), 72 + (pitch % 12)

    return None, None

def note_name(pitch):
    note = NOTE_NAMES[pitch % 12]
    octave = pitch // 12 - 1
    return f"{note}{octave}"

# ==============================
# PLAY ENGINE
# ==============================
def play(midi):
    global play_state
    play_state = "playing"
    print("▶ Playing (22-key piano | unlimited octave)")

    for msg in midi:
        while play_state == "pause":
            time.sleep(0.1)

        if play_state != "playing":
            break

        time.sleep(msg.time)

        if not midi_playable(msg):
            continue

        original_pitch = msg.note
        key, play_pitch = pitch_to_key(original_pitch)

        if not key:
            continue

        print(
            f"original key: {note_name(original_pitch)}({original_pitch}) "
            f"Play key: {note_name(play_pitch)}({play_pitch}) "
            f"Press: {key.upper()}"
        )

        keyboard.send(key)

# ==============================
# TOGGLE CONTROL
# ==============================
def toggle_play(midi):
    global play_state

    if play_state == "playing":
        play_state = "pause"
        print("⏸ Paused")

    elif play_state == "pause":
        play_state = "playing"
        print("▶ Resumed")

    elif play_state == "idle":
        print("▶ Start")
        keyboard.call_later(play, args=(midi,), delay=0.2)

# ==============================
# MAIN (CONFIG.JSON)
# ==============================
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="22-key Piano MIDI Player (Unlimited Octave)"
    )
    parser.add_argument(
        "config", nargs="?", type=str,
        help="path to config.json"
    )
    args = parser.parse_args()

    config_path = args.config or os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        "config.json"
    )

    if not os.path.exists(config_path):
        print("❌ config.json not found")
        exit()

    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    folder = config.get("folder_path")
    song = config.get("song_file")

    if not folder or not song:
        print("❌ Invalid config.json")
        exit()

    midi_path = os.path.join(folder, song)
    print("▶ Loading MIDI:", midi_path)

    midi = MidiFile(midi_path)

    print("\nControls:")
    print("  \\  → Start / Pause / Resume")
    print("  Backspace → Exit\n")

    keyboard.add_hotkey(
        "\\",
        lambda: toggle_play(midi),
        suppress=True,
        trigger_on_release=True
    )

    keyboard.wait("backspace", suppress=True)
