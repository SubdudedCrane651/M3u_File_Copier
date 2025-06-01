import os
import shutil
import tkinter as tk
from tkinter import filedialog
import threading
import itertools
import sys

def spinner(stop_event):
    """Displays a spinner animation while copying files."""
    for char in itertools.cycle(["|", "/", "-", "\\"]):
        if stop_event.is_set():  # Stop immediately when copying is done
            sys.stdout.write("\r✅ Files copied successfully! 🚀\n")
            sys.stdout.flush()
            break
        sys.stdout.write(f"\rCopying files... {char}")
        sys.stdout.flush()
        stop_event.wait(0.1)  # Checks frequently to stop cleanly

def copy_playlist_files():
    playlist_file = filedialog.askopenfilename(title="Select Playlist File", filetypes=[("M3U Files", "*.m3u")])
    source_dir = filedialog.askdirectory(title="Select Source Directory")
    dest_dir = filedialog.askdirectory(title="Select Destination Directory")

    if not playlist_file or not source_dir or not dest_dir:
        return

    with open(playlist_file, "r", encoding="utf-8") as file:
        lines = file.readlines()

    # Create and start spinner thread
    stop_spinner = threading.Event()
    spinner_thread = threading.Thread(target=spinner, args=(stop_spinner,))
    spinner_thread.start()

    for i in range(len(lines)):
        if lines[i].startswith("#EXTINF"):
            file_path = lines[i+1].strip().lstrip("\\")  # Ensure correct relative path
            full_source_path = os.path.join(source_dir, file_path)
            full_dest_path = os.path.join(dest_dir, file_path)

            if os.path.exists(full_source_path):
                os.makedirs(os.path.dirname(full_dest_path), exist_ok=True)
                shutil.copy2(full_source_path, full_dest_path)

    # Stop spinner and wait for thread to exit
    stop_spinner.set()
    spinner_thread.join()  # Spinner stops immediately

# Set up GUI
root = tk.Tk()
root.title("Playlist File Copier")

btn_copy = tk.Button(root, text="Copy Playlist Files", command=copy_playlist_files)
btn_copy.pack(pady=20)

root.mainloop()