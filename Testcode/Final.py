import os
import time
import threading
import tkinter as tk
from tkinter import filedialog, ttk
from mido import MidiFile
import keyboard

# =========================
# KEY MAP (22 KEYS)
# =========================
KEY_MAP = {
    # Low
    48: ',', 49: 'l', 50: '.', 51: ';', 52: '/', 53: 'o',
    54: '0', 55: 'p', 56: '-', 57: '[', 58: '=', 59: ']',

    # Middle
    60: 'z', 61: 's', 62: 'x', 63: 'd', 64: 'c', 65: 'v',
    66: 'g', 67: 'b', 68: 'h', 69: 'n', 70: 'j', 71: 'm',

    # High
    72: 'q', 73: '2', 74: 'w', 75: '3', 76: 'e', 77: 'r',
    78: '5', 79: 't', 80: '6', 81: 'y', 82: '7', 83: 'u',
    84: 'i'
}

NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F',
              'F#', 'G', 'G#', 'A', 'A#', 'B']

# =========================
# STATE
# =========================
play_state = "idle"
song_folder = ""
song_path = None
current_song_name = ""

# =========================
# UTIL
# =========================
def note_name(pitch):
    return f"{NOTE_NAMES[pitch % 12]}{pitch//12 - 1}"

def log(msg):
    terminal.insert("end", msg + "\n")
    terminal.see("end")

def calibrate_pitch(pitch):
    while pitch < 48:
        pitch += 12
    while pitch > 84:
        pitch -= 12
    return pitch

# =========================
# PLAYER
# =========================
def play_thread():
    global play_state

    if not song_path:
        log("⚠ No song selected")
        play_state = "idle"
        return

    midi = MidiFile(song_path)  # โหลดใหม่ทุกครั้ง
    play_state = "playing"
    log(f"▶ Playing: {current_song_name}")

    for msg in midi:
        if play_state == "idle":
            break

        while play_state == "pause":
            time.sleep(0.1)

        time.sleep(msg.time)

        if msg.type != 'note_on' or msg.velocity == 0:
            continue

        original = msg.note
        pitch = calibrate_pitch(original)

        if pitch not in KEY_MAP:
            continue

        key = KEY_MAP[pitch]

        log(
            f"original key: {note_name(original)}({original}) "
            f"Play key: {note_name(pitch)}({pitch}) "
            f"Press: {key.upper()}"
        )

        keyboard.press(key)
        time.sleep(0.04)
        keyboard.release(key)

    play_state = "idle"
    log("■ Finished")

def toggle_play():
    global play_state

    if play_state == "idle":
        threading.Thread(target=play_thread, daemon=True).start()

    elif play_state == "playing":
        play_state = "pause"
        log("⏸ Pause")

    elif play_state == "pause":
        play_state = "playing"
        log("▶ Resume")

def reset_player():
    global play_state, song_path, current_song_name
    play_state = "idle"
    song_path = None
    current_song_name = ""
    song_var.set("")
    status_label.config(text="No song selected")
    terminal.delete("1.0", "end")
    log("🔄 Reset complete")

# =========================
# FILE CONTROL
# =========================
def browse_folder():
    global song_folder
    song_folder = filedialog.askdirectory()
    if not song_folder:
        return

    songs = [f for f in os.listdir(song_folder) if f.lower().endswith(".mid")]
    song_menu["values"] = songs
    song_var.set("")
    log(f"📂 Folder: {song_folder}")
    log(f"🎵 Found {len(songs)} songs")

def open_folder():
    if song_folder:
        os.startfile(song_folder)

def select_song():
    global song_path, current_song_name

    if not song_folder:
        log("⚠ No folder selected")
        return

    name = song_var.get()
    if not name:
        log("⚠ No song chosen")
        return

    song_path = os.path.join(song_folder, name)
    current_song_name = name

    status_label.config(
        text=f"Selected: {name}  |  Press \\ to play",
        fg="lime"
    )
    log(f"✅ Selected song: {name}")
    log("▶ Press \\ to start")

# =========================
# UI
# =========================
root = tk.Tk()
root.title("Piano 22-Key MIDI Player")
root.geometry("780x540")

top = tk.Frame(root)
top.pack(pady=6)

tk.Button(top, text="📂 Browse Folder", command=browse_folder).pack(side="left", padx=5)
tk.Button(top, text="📁 Open Folder", command=open_folder).pack(side="left", padx=5)

song_var = tk.StringVar()
song_menu = ttk.Combobox(top, textvariable=song_var, state="readonly", width=38)
song_menu.pack(side="left", padx=5)

tk.Button(top, text="✅ Select Song", command=select_song).pack(side="left", padx=5)
tk.Button(top, text="🔄 Reset", command=reset_player).pack(side="left", padx=5)

status_label = tk.Label(
    root,
    text="No song selected",
    fg="yellow"
)
status_label.pack(pady=4)

terminal = tk.Text(root, height=18, bg="black", fg="lime")
terminal.pack(fill="both", padx=10, pady=10)

log("Controls:")
log("1) Browse Folder")
log("2) Select Song")
log("3) Press \\ to Play / Pause (works in game)")

# 🔑 GLOBAL HOTKEY (สำคัญ)
keyboard.add_hotkey("\\", toggle_play)

root.mainloop()
