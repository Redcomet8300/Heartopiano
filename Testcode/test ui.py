import tkinter as tk
from tkinter import ttk, filedialog
import os
import keyboard
import subprocess

# ---------------- State ----------------
song_folder = ""
song_list = []
play_state = "idle"

# ---------------- UI Functions ----------------
def log(msg):
    terminal.configure(state="normal")
    terminal.insert(tk.END, msg + "\n")
    terminal.see(tk.END)
    terminal.configure(state="disabled")

def browse_folder():
    global song_folder, song_list
    folder = filedialog.askdirectory()
    if not folder:
        return

    song_folder = folder
    song_list = [f for f in os.listdir(folder) if f.lower().endswith(".mid")]
    song_list.sort()

    dropdown["values"] = song_list
    if song_list:
        song_var.set(song_list[0])

    log(f"Loaded {len(song_list)} song(s)")
    log(f"Folder: {song_folder}")

def open_folder():
    if not song_folder:
        log("⚠ No song folder selected")
        return

    os.startfile(song_folder)


def toggle_play():
    global play_state
    if play_state == "playing":
        play_state = "paused"
        log("⏸ Paused")
    else:
        play_state = "playing"
        log("▶ Playing")
        # mock note output
        log("original key: F#4(66) Play key: F#4(66) Press: G")

# ---------------- Hotkey ----------------
keyboard.add_hotkey("\\", toggle_play)

# ---------------- UI ----------------
root = tk.Tk()
root.title("Heartopia / Naraka Piano Autoplay")
root.geometry("720x460")

# Top Frame
top = ttk.Frame(root)
top.pack(fill="x", padx=10, pady=10)

browse_btn = ttk.Button(top, text="Browse Song Folder", command=browse_folder)
browse_btn.pack(side="left")

open_btn = ttk.Button(top, text="Open Song Folder", command=open_folder)
open_btn.pack(side="left", padx=5)

song_var = tk.StringVar()
dropdown = ttk.Combobox(top, textvariable=song_var, state="readonly", width=35)
dropdown.pack(side="left", padx=10)

play_label = ttk.Label(top, text="Press \\ to Play / Pause")
play_label.pack(side="right")

# Terminal
terminal = tk.Text(
    root,
    height=16,
    bg="black",
    fg="lime",
    font=("Consolas", 10),
    state="disabled"
)
terminal.pack(fill="both", expand=True, padx=10, pady=10)

log("Ready.")
log("Press \\ to Play / Pause")

root.mainloop()
