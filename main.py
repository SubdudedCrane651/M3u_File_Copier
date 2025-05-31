import os
import shutil
import tkinter as tk
from tkinter import filedialog

def copy_playlist_files():
    playlist_file = filedialog.askopenfilename(title="Select Playlist File", filetypes=[("M3U Files", "*.m3u")])
    source_dir = filedialog.askdirectory(title="Select Source Directory")
    dest_dir = filedialog.askdirectory(title="Select Destination Directory")

    if not playlist_file or not source_dir or not dest_dir:
        return

    with open(playlist_file, "r", encoding="utf-8") as file:
        lines = file.readlines()
    
    for i in range(len(lines)):
        if lines[i].startswith("#EXTINF"):
            file_path = lines[i+1].strip()
            full_source_path = os.path.join(source_dir, file_path.lstrip("\\"))
            full_dest_path = os.path.join(dest_dir, file_path.lstrip("\\"))

            if os.path.exists(full_source_path):
                os.makedirs(os.path.dirname(full_dest_path), exist_ok=True)
                shutil.copy2(full_source_path, full_dest_path)
    print(full_dest_path)
    print("Files copied successfully!")

# Set up GUI
root = tk.Tk()
root.title("Playlist File Copier")

btn_copy = tk.Button(root, text="Copy Playlist Files", command=copy_playlist_files)
btn_copy.pack(pady=20)

root.mainloop()