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

    def clean_mp3(self, input_path, output_path):
        try:
            subprocess.run([
                "c:\\ffmpeg\\bin\\ffmpeg",
                "-y",  # Overwrite without asking
                "-i", input_path,
                "-map_metadata", "-1",  # Remove all metadata
                "-codec:a", "libmp3lame",
                "-qscale:a", "2",  # High quality
                output_path
            ], check=True)
            print(f"✅ Cleaned: {os.path.basename(input_path)}")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed: {os.path.basename(input_path)}\n{e}")

    def embed_image(self):
        if not self.mp3_path or not self.jpg_path:
            QMessageBox.warning(self, "Missing Files", "Please select both an MP3 and a JPG image.")
            return

        try:

            self.clean_mp3(self.mp3_path, "D:\\Music\\cleaned.mp3")
            
            original_path = self.mp3_path
            if os.path.exists(original_path):
                os.remove(original_path)
                print(f"🗑️ Deleted: {original_path}")
            else:
                print(f"⚠️ File not found: {original_path}")
           
            try:
                #pass
                shutil.copy2("D:\\Music\\cleaned.mp3", self.mp3_path)
            except Exception as e:
                print(f"❌ Failed to copy: {e}")

            audiofile = eyed3.load(self.mp3_path)

            # Step 1: Backup metadata
            title = audiofile.tag.title
            artist = audiofile.tag.artist
            album = audiofile.tag.album
            genre = audiofile.tag.genre.name if audiofile.tag.genre else None
            year = audiofile.tag.getBestDate()
            track_num = audiofile.tag.track_num[0] if audiofile.tag.track_num else None

            # Step 2: Clear all tags (removes images too)
            audiofile.tag.clear()
            audiofile.tag.save()

            # Step 3: Rebuild metadata
            audiofile.tag.title = title
            audiofile.tag.artist = artist
            audiofile.tag.album = album
            if genre:
                audiofile.tag.genre = genre
            if year:
                audiofile.tag.release_date = year
            if track_num:
                audiofile.tag.track_num = track_num

            audiofile.tag.save()

            audio = MP3(self.mp3_path, ID3=ID3)
            if audio.tags is None:
                audio.add_tags()                         

            # Embed new image
            with open(self.jpg_path, 'rb') as img:
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
            
            QMessageBox.information(self, "Success", "Image embedded successfully into MP3.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to embed image:\n{str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MP3CoverEmbedder()
    window.show()
    sys.exit(app.exec_())