import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QLabel,
    QFileDialog, QMessageBox
)
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, error

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

    def embed_image(self):
        if not self.mp3_path or not self.jpg_path:
            QMessageBox.warning(self, "Missing Files", "Please select both an MP3 and a JPG image.")
            return

        try:
            audio = MP3(self.mp3_path, ID3=ID3)
            try:
                audio.add_tags()
            except error:
                pass

            with open(self.jpg_path, 'rb') as img:
                audio.tags.add(
                    APIC(
                        encoding=3,         # UTF-8
                        mime='image/jpeg',
                        type=3,             # Front cover
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