import os
os.environ['QT_QPA_PLATFORM'] = 'xcb'
import shutil
import zipfile
import tempfile
import subprocess
from PyQt5.QtGui import QFont
from PyQt5.QtCore import QSize, QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QTextBrowser, QWidget, QVBoxLayout, QPushButton, QLabel


# UPDATE CARDSFOLDER
class GitCloneWorker(QThread):
    update_message = pyqtSignal(str)

    def __init__(self, repo_url, temp_dir, parent=None):
        super().__init__()
        self.repo_url = repo_url
        self.temp_dir = temp_dir

    def run(self):
        process = subprocess.Popen(["git", "clone", self.repo_url, self.temp_dir], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        
        while True:
            output = process.stdout.readline()
            if not output and process.poll() is not None:
                break
            if output:
                self.update_message.emit(output.decode('utf-8').strip())

class UpdateCardsfolderWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent  # Store the parent widget to switch back to it later
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        update_cardsfolder_create_backup_label = QLabel("\t\t\t\t\t\t\t\t\t[-- Choose to Update the cardsfolder or Create a Backup --]")
        self.set_font(update_cardsfolder_create_backup_label, 'Arial', 13)        
        layout.addWidget(update_cardsfolder_create_backup_label)

        button_size = QSize(1340, 100) 

        self.message_box = QTextBrowser()
        self.message_box.setFixedHeight(200)  # Set a fixed height for the message box
        self.message_box.setText("Progress window...")
        layout.addWidget(self.message_box)
        
        update_button = QPushButton("Update Cardsfolder")
        self.set_font(update_button, 'Arial', 13)
        update_button.setFixedSize(button_size)
        update_button.clicked.connect(self.update_cardsfolder)
        layout.addWidget(update_button)

        btn_create_backup = QPushButton("Create Backup", self)
        self.set_font(btn_create_backup, 'Arial', 13)
        btn_create_backup.setFixedSize(button_size)        
        btn_create_backup.clicked.connect(self.create_backup)
        layout.addWidget(btn_create_backup)

        exit_button = QPushButton("Exit")
        exit_button.setFixedSize(button_size)
        self.set_font(exit_button, 'Arial', 13)
        exit_button.clicked.connect(QApplication.quit)
        layout.addWidget(exit_button)
        
        self.setLayout(layout)        

    def set_font(self, widget, font_name, font_size):
        font = QFont(font_name, font_size)
        widget.setFont(font)

    def update_cardsfolder(self):
        CARDSFOLDER_DIR = "./app/res/cardsfolder"
        TARGET_DIR = "./app/res"
        REPO_URL = "https://github.com/Card-Forge/forge.git"
        DIRECTORY = "forge-gui/res/cardsfolder"
    
        if os.path.exists(CARDSFOLDER_DIR):
            shutil.rmtree(CARDSFOLDER_DIR)

        # Create a temporary directory
        with tempfile.TemporaryDirectory() as TEMP_DIR:
            self.message_box.setText(f"Cloning repository into {TEMP_DIR}...")
            
            worker = GitCloneWorker(REPO_URL, TEMP_DIR)
            worker.update_message.connect(self.update_progress)
            worker.start()

            while worker.isRunning():
                QApplication.processEvents()

            # Ensure the target directory exists
            os.makedirs(TARGET_DIR, exist_ok=True)

            # Define the full path of the directory to be copied
            source_path = os.path.join(TEMP_DIR, DIRECTORY)
            destination_path = os.path.join(TARGET_DIR, "cardsfolder")

            self.message_box.setText(f"Copying {source_path} to {destination_path}")
        
            # Copy the desired directory to the target location
            shutil.copytree(source_path, destination_path)

        self.message_box.setText("Cardsfolder update complete...")

    def update_progress(self, message):
        self.message_box.append(message)  # Append instead of setText to show live progress

    def create_backup(self):
        directory_path = "/mnt/Data/coding_projects/python/forgeBuilderApp/forgeScriptSearch_DeckBuilder"
        output_zip = "/mnt/Data/coding_projects/python/forgeScriptSearch_DeckBuilder_PyQt_BKP.zip"

        if not os.path.exists(directory_path):
            self.message_box.setText(f"The directory {directory_path} does not exist.")
            return
        
        with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(directory_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    zipf.write(file_path, os.path.relpath(file_path, directory_path))

        self.message_box.setText("Backup complete...")