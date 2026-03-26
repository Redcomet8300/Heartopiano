import os
import argparse
import time
import json
from mido import MidiFile
import keyboard

# ==============================
# NOTE DEFINITIONS
# ==============================
NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F',
              'F#', 'G', 'G#', 'A', 'A#', 'B']

# Heartopia key layout
NORMAL_MAP = {
    'C': 'q', 'D': 'w', 'E': 'e', 'F': 'r',
    'G': 't', 'A': 'y', 'B': 'u'
}

DEEP_MAP = {
    'C': 'a', 'D': 's', 'E': 'd', 'F': 'f',
    'G': 'g', 'A': 'h', 'B': 'j'
}

HIGH_DO_KEY = 'i'  # C5

# ==============================
# PLAY STATE
# ==============================
play_state = 'idle'

# ==============================
# MIDI FILTER
# ==============================
def midi_playable(event):
    return (
        not event.is_meta
        and event.type == 'note_on'
        and event.velocity > 0
    )

# ==============================
# SHARP → NEAREST NATURAL
# ==============================
def nearest_natural_note(pitch):
    idx = pitch % 12

    # already natural
    if NOTE_NAMES[idx] in NORMAL_MAP:
        return pitch

    SHARP_TO_NATURAL = {
        1: 0,   # C# -> C
        3: 4,   # D# -> E
        6: 5,   # F# -> F
        8: 7,   # G# -> G
        10: 9   # A# -> A
    }

    if idx in SHARP_TO_NATURAL:
        return pitch - (idx - SHARP_TO_NATURAL[idx])

    return pitch

# ==============================
# NOTE → KEY (SINGLE NOTE)
# ==============================
def note_to_key(pitch):
    pitch = nearest_natural_note(pitch)

    note = NOTE_NAMES[pitch % 12]
    octave = pitch // 12 - 1

    # snap octave
    if octave < 3:
        octave = 3
    elif octave > 5:
        octave = 5

    if octave <= 3:
        return DEEP_MAP.get(note)

    if octave >= 5 and note == 'C':
        return HIGH_DO_KEY

    return NORMAL_MAP.get(note)

# ==============================
# CHORD HANDLING
# ==============================
def is_chord(notes):
    return len(notes) >= 2

def chord_to_key(notes):
    """
    Chord → play lowest note with DEEP_MAP
    """
    lowest = min(notes)
    pitch = nearest_natural_note(lowest)
    note = NOTE_NAMES[pitch % 12]
    return DEEP_MAP.get(note)

# ==============================
# PLAY ENGINE
# ==============================
def play(midi):
    global play_state
    play_state = 'playing'
    print("▶ Start playing")

    pending_notes = []

    for event in midi:
        if play_state != 'playing':
            break

        # time step → resolve note / chord
        if event.time > 0:
            if pending_notes:
                # 🎶 CHORD
                if is_chord(pending_notes):
                    key = chord_to_key(pending_notes)
                    if key:
                        keyboard.press(key)
                        time.sleep(0.04)
                        keyboard.release(key)

                # 🎵 SINGLE NOTE
                else:
                    key = note_to_key(pending_notes[0])
                    if key:
                        keyboard.press(key)
                        time.sleep(0.03)
                        keyboard.release(key)

                pending_notes.clear()

            time.sleep(event.time)

        if not midi_playable(event):
            continue

        pending_notes.append(event.note)

        # safety limit
        if len(pending_notes) > 4:
            pending_notes = pending_notes[:4]

    # last notes
    if pending_notes:
        if is_chord(pending_notes):
            key = chord_to_key(pending_notes)
        else:
            key = note_to_key(pending_notes[0])

        if key:
            keyboard.press(key)
            time.sleep(0.03)
            keyboard.release(key)

# ==============================
# CONTROL (PAUSE / RESUME)
# ==============================
def control(midi):
    global play_state

    if play_state == 'playing':
        play_state = 'pause'
        print("⏸ Paused")

    elif play_state in ('pause', 'idle'):
        print("▶ Resumed")
        keyboard.call_later(play, args=(midi,), delay=0.3)

# ==============================
# MAIN
# ==============================
if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Heartopia MIDI Auto Player'
    )
    parser.add_argument(
        'config', nargs="?", type=str,
        help='path to config JSON file'
    )
    args = parser.parse_args()

    # Load config.json
    config_path = args.config
    if not config_path:
        config_path = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            'config.json'
        )

    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)

    folder_path = config.get('folder_path')
    song_file = config.get('song_file')

    if not folder_path or not song_file:
        print("❌ Invalid config.json")
        exit()

    midi_path = os.path.join(folder_path, song_file)

    print("Trying to open MIDI file:")
    print(midi_path)

    midi = MidiFile(midi_path)

    print("\nControls:")
    print("  \\  → Play / Pause")
    print("  Backspace → Exit\n")

    keyboard.add_hotkey(
        '\\',
        lambda: control(midi),
        suppress=True,
        trigger_on_release=True
    )

    keyboard.wait('backspace', suppress=True)
