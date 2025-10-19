import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QListWidget,
    QFileDialog, QComboBox, QMessageBox, QLabel, QHBoxLayout
)
from mutagen.mp3 import MP3

class M3UEditor(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("M3U Playlist Editor")
        self.resize(600, 500)

        self.layout = QVBoxLayout()
        self.label = QLabel("Playlist Tracks:")
        self.file_list = QListWidget()

        # Buttons
        self.button_layout = QHBoxLayout()
        self.load_button = QPushButton("Load .m3u")
        self.add_button = QPushButton("Add MP3 Files")
        self.delete_button = QPushButton("Delete Selected")
        self.save_button = QPushButton("Save .m3u")

        # Sorting
        self.sort_box = QComboBox()
        self.sort_box.addItems(["Filename A-Z", "Filename Z-A", "Date Modified", "File Size"])

        # Assemble layout
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.file_list)
        self.layout.addWidget(self.sort_box)
        self.button_layout.addWidget(self.load_button)
        self.button_layout.addWidget(self.add_button)
        self.button_layout.addWidget(self.delete_button)
        self.button_layout.addWidget(self.save_button)
        self.layout.addLayout(self.button_layout)
        self.setLayout(self.layout)

        # Connect actions
        self.load_button.clicked.connect(self.load_playlist)
        self.add_button.clicked.connect(self.add_files)
        self.delete_button.clicked.connect(self.delete_selected)
        self.save_button.clicked.connect(self.save_playlist)
        self.sort_box.currentIndexChanged.connect(self.sort_files)

    def add_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select MP3 Files", "", "Audio Files (*.mp3)")
        for file in files:
            if file not in [self.file_list.item(i).text() for i in range(self.file_list.count())]:
                self.file_list.addItem(file)

    def delete_selected(self):
        for item in self.file_list.selectedItems():
            self.file_list.takeItem(self.file_list.row(item))

    def sort_files(self):
        items = [self.file_list.item(i).text() for i in range(self.file_list.count())]
        sort_type = self.sort_box.currentText()

        if sort_type == "Filename A-Z":
            items.sort()
        elif sort_type == "Filename Z-A":
            items.sort(reverse=True)
        elif sort_type == "Date Modified":
            items.sort(key=lambda x: os.path.getmtime(x))
        elif sort_type == "File Size":
            items.sort(key=lambda x: os.path.getsize(x))

        self.file_list.clear()
        for item in items:
            self.file_list.addItem(item)

    def load_playlist(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open Playlist", "", "Playlist Files (*.m3u)")
        if not path:
            return

        try:
            with open(path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            self.file_list.clear()
            for line in lines:
                line = line.strip()
                if line and not line.startswith("#"):
                    self.file_list.addItem(os.path.normpath(line))
            QMessageBox.information(self, "Loaded", f"Loaded playlist:\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load playlist:\n{str(e)}")

    def save_playlist(self):
        if self.file_list.count() == 0:
            QMessageBox.warning(self, "No Files", "Add or load MP3 files first.")
            return

        dialog = QFileDialog(self)
        dialog.setAcceptMode(QFileDialog.AcceptSave)
        dialog.setNameFilter("Playlist Files (*.m3u)")
        dialog.setDefaultSuffix("m3u")
        if dialog.exec_():
            path = dialog.selectedFiles()[0]
        else:
            return

        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write("#EXTM3U\n")
                for i in range(self.file_list.count()):
                    file_path = self.file_list.item(i).text()
                    try:
                        audio = MP3(file_path)
                        duration = int(audio.info.length)
                    except Exception:
                        duration = -1
                    title = os.path.basename(file_path)
                    f.write(f"#EXTINF:{duration},{title}\n")
                    f.write(os.path.normpath(file_path) + "\n")
            QMessageBox.information(self, "Saved", f"Playlist saved to:\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save playlist:\n{str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = M3UEditor()
    window.show()
    sys.exit(app.exec_())