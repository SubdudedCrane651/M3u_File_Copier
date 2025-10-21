import sys
import os
import subprocess
import shutil
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QLabel,
    QFileDialog, QMessageBox
)
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, TIT2, TPE1, TALB, TCON, TDRC, TRCK, error
import eyed3


class MP3CoverEmbedder(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MP3 Album Art Embedder")
        self.resize(500, 200)

        self.layout = QVBoxLayout()
        self.mp3_label = QLabel("No MP3 selected")
        self.jpg_label = QLabel("No image selected")

        self.select_mp3_btn = QPushButton("Choose MP3 File")
        self.select_jpg_btn = QPushButton("Choose JPG Image")
        self.embed_btn = QPushButton("Embed Image into MP3")

        self.layout.addWidget(self.mp3_label)
        self.layout.addWidget(self.select_mp3_btn)
        self.layout.addWidget(self.jpg_label)
        self.layout.addWidget(self.select_jpg_btn)
        self.layout.addWidget(self.embed_btn)
        self.setLayout(self.layout)

        self.select_mp3_btn.clicked.connect(self.select_mp3)
        self.select_jpg_btn.clicked.connect(self.select_jpg)
        self.embed_btn.clicked.connect(self.embed_image)

        self.mp3_path = None
        self.jpg_path = None

    def select_mp3(self):
        file, _ = QFileDialog.getOpenFileName(self, "Select MP3 File", "", "Audio Files (*.mp3)")
        if file:
            self.mp3_path = file
            self.mp3_label.setText(f"MP3: {os.path.basename(file)}")

    def select_jpg(self):
        file, _ = QFileDialog.getOpenFileName(self, "Select JPG Image", "", "Image Files (*.jpg *.jpeg)")
        if file:
            self.jpg_path = file
            self.jpg_label.setText(f"Image: {os.path.basename(file)}")

    def clean_mp3(self,input_path, output_path):
        subprocess.run([
            "c:\\ffmpeg\\bin\\ffmpeg",
            "-y",
            "-i", input_path,
            "-map_metadata", "-1",  # Strip all metadata
            "-id3v2_version", "3",  # Force clean ID3v2.3
            "-write_id3v1", "0",    # Disable ID3v1
            "-codec:a", "libmp3lame",
            "-qscale:a", "2",
            output_path
        ], check=True)

    def embed_image(self):
        if not self.mp3_path or not self.jpg_path:
            QMessageBox.warning(self, "Missing Files", "Please select both an MP3 and a JPG image.")
            return

        try:
            
            # Step 1: Load and extract existing metadata
            audio = MP3(self.mp3_path, ID3=ID3)
            tags = audio.tags

            # Backup key fields
            title = tags.get("TIT2")
            artist = tags.get("TPE1")
            album = tags.get("TALB")
            genre = tags.get("TCON")
            year = tags.get("TDRC")
            track = tags.get("TRCK")
            
            self.clean_mp3(self.mp3_path, "D:\\Music\\cleaned.mp3")

            # Step 2: Delete all tags
            #audio.delete()
            #audio.save()

            # Step 3: Recreate tags only (no image yet)
            audio = MP3("D:\\Music\\cleaned.mp3", ID3=ID3)
            if audio.tags is None:
                audio.add_tags()

            # Recreate metadata tags
            if title: audio.tags.add(TIT2(encoding=3, text=title.text))
            if artist: audio.tags.add(TPE1(encoding=3, text=artist.text))
            if album: audio.tags.add(TALB(encoding=3, text=album.text))
            if genre: audio.tags.add(TCON(encoding=3, text=genre.text))
            if year: audio.tags.add(TDRC(encoding=3, text=year.text))
            if track: audio.tags.add(TRCK(encoding=3, text=track.text))
            
            audio.save()
            
            audio = MP3(self.mp3_path, ID3=ID3)
            if audio.tags is None:
                audio.add_tags()                         

            # Embed new image
            with open("D:\\Music\\cleaned.mp3", 'rb') as img:
                audio.tags.add(
                    APIC(
                        encoding=3,
                        mime='image/jpeg',
                        type=3,
                        desc='Cover',
                        data=img.read()
                    )
                )

            audio.save()
            
            try:
                #pass
                shutil.copy2("D:\\Music\\cleaned.mp3", self.mp3_path)
            except Exception as e:
                print(f"❌ Failed to copy: {e}")
                
            QMessageBox.information(self, "Success", "Image embedded successfully into MP3.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to embed image:\n{str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MP3CoverEmbedder()
    window.show()
    sys.exit(app.exec_())