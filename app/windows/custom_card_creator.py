import os
os.environ['QT_QPA_PLATFORM'] = 'xcb'
from pathlib import Path
from collections import OrderedDict
from PyQt5.QtGui import QFont,QPixmap
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QSplitter, QTabWidget, QHBoxLayout, 
                             QComboBox, QMessageBox, 
                             QApplication, QWidget, QVBoxLayout, QPushButton, 
                             QLineEdit, QLabel, QTextEdit, QCheckBox, QFileDialog)
from app.windows.script_search_worker import ScriptSearchWorker

# CUSTOM CARD CREATOR
class CustomCardCreatorWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.selected_lines = OrderedDict()  # Retains order of selected lines
        self.oracle_texts = OrderedDict()   # Stores Oracle texts for each line
        self.text_edit = QTextEdit()
        # Main layout
        main_layout = QVBoxLayout()
        
        # Tab widget to switch between selecting lines and creating a custom set
        tab_widget = QTabWidget()
        
        # Left side tab for selecting lines
        tab_1 = QWidget()
        tab_1_layout = QVBoxLayout()
        
        # Splitter to divide the left tab into two parts
        splitter = QSplitter(Qt.Horizontal)
        
        # Search related widgets and layout
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.set_font(self.search_input, 'Arial', 13)
        self.search_input.setPlaceholderText("Enter search query")
        search_layout.addWidget(self.search_input)        
        self.search_button = QPushButton("Search")
        self.set_font(self.search_button, 'Arial', 13)
        self.search_button.clicked.connect(self.on_search)
        search_layout.addWidget(self.search_button)
        tab_1_layout.addLayout(search_layout)

        # Connect returnPressed signal to the search function
        self.search_input.returnPressed.connect(self.on_search)

        self.checkbox_cardsfolder = QCheckBox("Search in ./app/res/cardsfolder")
        tab_1_layout.addWidget(self.checkbox_cardsfolder)
        self.checkbox_custom_created_cards = QCheckBox("Search in ./app/custom_created/cards")
        tab_1_layout.addWidget(self.checkbox_custom_created_cards)

        self.strict_search_checkbox = QCheckBox("Strict Search")
        tab_1_layout.addWidget(self.strict_search_checkbox)

        # Connect the checkboxes to a slot that updates the directories
        self.checkbox_cardsfolder.stateChanged.connect(self.update_search_directories)
        self.checkbox_custom_created_cards.stateChanged.connect(self.update_search_directories)

        # Left part of the splitter (display and save selected lines)
        tab_1_split_part = QWidget()
        tab_1_split_layout = QVBoxLayout()
        tab_1_split_part.setFixedWidth(700)  # Adjust this value as needed
        
        # Left part display results
        self.display_lines_list = QTextEdit()
        self.display_lines_list.setReadOnly(True)
        self.populate_selected_lines()
        tab_1_split_layout.addWidget(self.display_lines_list)
        
        # Left part area to copy and paste results
        self.selected_lines_display = QTextEdit()
        self.selected_lines_display.setReadOnly(False)
        tab_1_split_layout.addWidget(self.selected_lines_display)

        save_button = QPushButton("Create Card")
        self.set_font(save_button, 'Arial', 13)
        save_button.clicked.connect(self.save_card_script)
        tab_1_split_layout.addWidget(save_button)

        exit_button = QPushButton("Exit")     
        self.set_font(exit_button, 'Arial', 13)
        exit_button.clicked.connect(QApplication.quit)
        tab_1_split_layout.addWidget(exit_button)
        
        tab_1_split_part.setLayout(tab_1_split_layout)
        
        # Right part of the splitter (new input fields with checkboxes and display area)
        tab_2_split_part = QWidget()
        tab_2_split_layout = QVBoxLayout()

        # Directory selection combobox for images
        self.image_directory_combobox = QComboBox()
        self.populate_image_directory_combobox()
        tab_2_split_layout.addWidget(QLabel("[-- Choose Image Folder --]"))
        tab_2_split_layout.addWidget(self.image_directory_combobox)

        # Image display setup
        self.image_display_label = QLabel()  # Using QLabel for simplicity
        self.image_display_label.setFixedSize(450, 650)  # Set size as needed
        self.image_display_label.setStyleSheet("border: 1px solid black;")
        tab_2_split_layout.addWidget(self.image_display_label)

        tab_2_split_part.setLayout(tab_2_split_layout)

        splitter.addWidget(tab_1_split_part)
        splitter.addWidget(tab_2_split_part)

        tab_1_layout.addWidget(splitter)        
        tab_1.setLayout(tab_1_layout)
        
        # Right side tab for creating custom set
        tab_2 = QWidget()
        tab_2_layout = QVBoxLayout()        
        self.create_custom_set_section(tab_2_layout)        
        tab_2.setLayout(tab_2_layout)
        
        # Add tabs to the tab widget
        tab_widget.addTab(tab_1, "Create Custom Card")
        tab_widget.addTab(tab_2, "Create Custom Set")

        main_layout.addWidget(tab_widget)
        
        self.setLayout(main_layout)
        
        # Oracle: checkbox and display
        self.oracle_display = QTextEdit()
        self.oracle_display.setReadOnly(False)
        
        # Initialize SearchWorker
        self.worker = ScriptSearchWorker(Path('./app/res/cardsfolder'), "")
        self.worker.resultReady.connect(self.on_search_results_ready)

        # Connect image directory combobox to update image display
        self.image_directory_combobox.currentIndexChanged.connect(self.update_image_display)

    def get_all_subdirectories(self, base_path):
        subdirectories = []
        for root, dirs, files in os.walk(base_path):
            for dir_name in dirs:
                subdirectories.append(os.path.relpath(os.path.join(root, dir_name), base_path))
        return sorted(subdirectories)

    def populate_image_directory_combobox(self):
        base_path = './app/set_images/'
        if os.path.exists(base_path) and os.path.isdir(base_path):
            folders = self.get_all_subdirectories(base_path)
            self.image_directory_combobox.addItems(folders)

        # Initialize the image files list and current index
        self.image_files = []
        self.current_image_index = 0

        # Connect image directory combobox to update image display
        self.image_directory_combobox.currentIndexChanged.connect(self.update_image_display_and_files)

    def update_image_display_and_files(self):
        selected_folder = self.image_directory_combobox.currentText()
        images_dir = os.path.join('./app/set_images/', selected_folder)
        
        if not os.path.exists(images_dir) or not os.listdir(images_dir):  # Check if the directory exists and has files
            self.image_display_label.setText("Directory is empty or does not exist.")
            return
        
        image_files = [f for f in os.listdir(images_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        
        if not image_files:  # Check if there are any image files in the directory
            self.image_display_label.setText("No image found.")
            return
        
        self.image_files = [os.path.join(images_dir, img) for img in image_files]
        self.current_image_index = 0
        self.update_image_display()

    def update_image_display(self):
        if not self.image_files:
            self.image_display_label.setText("No image files available.")
            return

        image_path = self.image_files[self.current_image_index]
        
        pixmap = QPixmap(image_path)
        if not pixmap.isNull():  # Check if the pixmap is valid
            self.image_display_label.setPixmap(pixmap.scaled(self.image_display_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            self.image_display_label.setText("Failed to load image.")

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Left:
            self.current_image_index = (self.current_image_index - 1) % len(self.image_files)
            self.update_image_display()
        elif event.key() == Qt.Key_Right:
            self.current_image_index = (self.current_image_index + 1) % len(self.image_files)
            self.update_image_display()

    def set_font(self, widget, font_name, font_size):
        font = QFont(font_name, font_size)
        widget.setFont(font)

    def populate_selected_lines(self):
        input_file_path = './app/results/search-results.txt'
        if not os.path.exists(input_file_path):
            QMessageBox.warning(self, "Error", "File not found.")
            return
        
        with open(input_file_path, 'r') as file:
            lines = file.readlines()
        
        self.display_lines_list.setText(''.join(line for line in lines))
        
    def save_card_script(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Card Script", "./app/custom_created/cards/", "Text Files (*.txt)")
        if file_path:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(self.text_edit.toPlainText())
            QMessageBox.information(self, "Success", "Card script saved successfully.")

    def update_search_directories(self):
        self.search_directories = []
        if self.checkbox_cardsfolder.isChecked():
            self.search_directories.append('./app/res/cardsfolder')
        if self.checkbox_custom_created_cards.isChecked():
            self.search_directories.append('./app/custom_created/cards')

    def on_search(self):
        if not any([self.checkbox_cardsfolder.isChecked(), self.checkbox_custom_created_cards.isChecked()]):
            QMessageBox.warning(self, "Warning", "Please select at least one search directory.")
            return
        query = self.search_input.text()
        self.worker.query = query
        self.worker.search_paths = [Path(directory) for directory in self.search_directories]
        self.worker.strict_search_mode = self.strict_search_checkbox.isChecked()  # Pass the strict search mode
        self.worker.start()

    def on_search_results_ready(self, results):
        if not results:
            QMessageBox.warning(self, "No Matches Found", f"No matches found for any of the keywords: {self.worker.query}. Please try again.")
            return
        
        with open('./app/results/search-results.txt', 'w', encoding='utf-8') as f:
            f.writelines(result + '\n####\n\n' for result in results)
        self.display_lines_list.clear()  # Clear the current search results
        self.populate_selected_lines()

# CUSTOM SET CREATOR
    def create_custom_set_section(self, layout):
        main_layout = QHBoxLayout()
        
        # Create left side layout
        self.create_left_side_ui(main_layout)
        
        # Create right side layout
        self.create_right_side_ui(main_layout)
        
        layout.addLayout(main_layout)

    def create_left_side_ui(self, main_layout):
        custom_set_layout = QVBoxLayout()

        # Add a single QTextEdit widget with metadata parameters
        self.metadata_text_edit = QTextEdit()
        self.metadata_text_edit.setPlainText("""[metadata]
Code=
Date=
Name=
Type=
ScryfallCode=
Prerelease=
BoosterBox=
BoosterSlots=
Booster=

[cards]

[gain lands]

[alternate art]

[special guests]

[precon product]

[jumpstart]

[showcase]

[etched]

[borderless]

[extended art]

[buy a box]

[bundle]

[promo]

[dungeons]

[foils]

[backgrounds]

[legends]

[rebalanced]

[conjured]

[tokens]

[other]

# Put Custom Card Types
[BasicTypes]

[LandTypes]

[CreatureTypes]

[SpellTypes]

[EnchantmentTypes]

[ArtifactTypes]

[WalkerTypes]

[DungeonTypes]

[BattleTypes]

[PlanarTypes]
    """)
        custom_set_layout.addWidget(self.metadata_text_edit)

        # New Custom Set button
        new_custom_set_button = QPushButton("New Custom Set")
        self.set_font(new_custom_set_button, 'Arial', 13)
        new_custom_set_button.clicked.connect(self.new_custom_set)
        custom_set_layout.addWidget(new_custom_set_button)

        # Load Custom Set button
        load_custom_set_button = QPushButton("Load Custom Set")
        self.set_font(load_custom_set_button, 'Arial', 13)
        load_custom_set_button.clicked.connect(self.load_custom_set)
        custom_set_layout.addWidget(load_custom_set_button)

        # Save Current Edition Button
        save_button = QPushButton("Save Custom Set")
        self.set_font(save_button, 'Arial', 13)
        save_button.clicked.connect(self.save_current_edition_text)
        custom_set_layout.addWidget(save_button)


        main_layout.addLayout(custom_set_layout)

    def new_custom_set(self):
        # Refresh the QTextEdit window with default metadata parameters
        self.metadata_text_edit.setPlainText("""[metadata]
Code=
Date=
Name=
Type=
ScryfallCode=
Prerelease=
BoosterBox=
BoosterSlots=
Booster=

[cards]

[gain lands]

[alternate art]

[special guests]

[precon product]

[jumpstart]

[showcase]

[etched]

[borderless]

[extended art]

[buy a box]

[bundle]

[promo]

[dungeons]

[foils]

[backgrounds]

[legends]

[rebalanced]

[conjured]

[tokens]

[other]

# Put Custom Card Types
[BasicTypes]

[LandTypes]

[CreatureTypes]

[SpellTypes]

[EnchantmentTypes]

[ArtifactTypes]

[WalkerTypes]

[DungeonTypes]

[BattleTypes]

[PlanarTypes]
    """)

    def load_custom_set(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly

        # Set the directory to './app/custom_created/editions'
        directory = './app/custom_created/editions'

        file_name, _ = QFileDialog.getOpenFileName(self, "Select Custom Set File", directory, "Text Files (*.txt);;All Files (*)", options=options)

        if file_name:
            try:
                with open(file_name, 'r') as file:
                    content = file.read()
                    self.metadata_text_edit.setPlainText(content)
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to read file '{file_name}': {str(e)}")

    def save_current_edition_text(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ShowDirsOnly
        directory = './app/custom_created/editions'
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Current Edition", directory, "Text Files (*.txt);;All Files (*)", options=options)

        if file_name:
            try:
                with open(file_name, 'w') as file:
                    file.write(self.metadata_text_edit.toPlainText())
                QMessageBox.information(self, "Success", f"File saved successfully to {file_name}")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to save file '{file_name}': {str(e)}")

    def create_right_side_ui(self, main_layout):
        right_layout = QVBoxLayout()
        
        # Dropdown for folder selection
        self.folder_dropdown = QComboBox()
        self.populate_folder_dropdown()
        right_layout.addWidget(QLabel("[-- Select Folder to Display Created Cards --]"))
        right_layout.addWidget(self.folder_dropdown)
        
        # Display area for Custom Card tab
        self.custom_card_display = QTextEdit()
        self.custom_card_display.setReadOnly(True)
        right_layout.addWidget(QLabel("Card Names List:"))
        right_layout.addWidget(self.custom_card_display)
                
        main_layout.addLayout(right_layout)
            
    def populate_folder_dropdown(self):
        root_folder_path = './app/custom_created/cards'
        if os.path.exists(root_folder_path) and os.path.isdir(root_folder_path):
            folders = []
            
            # Recursively get all subdirectories
            for dirpath, dirnames, _ in os.walk(root_folder_path):
                # Get the relative path from root_folder_path to dirpath
                rel_path = os.path.relpath(dirpath, start=root_folder_path)
                if rel_path != '.':
                    folders.append(rel_path)
            
            self.folder_dropdown.addItems(folders)
        
        # Connect the dropdown's currentIndexChanged signal to a slot
        self.folder_dropdown.currentIndexChanged.connect(self.on_folder_changed)

    def on_enable_create_changed(self, state):
        if state == Qt.Checked:
            selected_index = self.folder_dropdown.currentIndex()
            self.on_folder_changed(selected_index)
        else:
            self.custom_card_display.clear()

    def on_folder_changed(self, index):
        selected_folder = self.folder_dropdown.itemText(index)
        if not selected_folder:
            return
        
        folder_path = os.path.join('./app/custom_created/cards', selected_folder)
        if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
            QMessageBox.warning(self, "Error", f"The selected path '{folder_path}' is not a valid directory.")
            return
        
        extracted_data = []
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            if os.path.isfile(file_path) and filename.endswith('.txt'):
                try:
                    with open(file_path, 'r') as file:
                        content = file.readlines()
                        name_value = None
                        for line in content:
                            line = line.strip()
                            if line.startswith('Name:'):
                                key_value = line.split(':')
                                if len(key_value) == 2:
                                    _, value = key_value
                                    name_value = value
                        if name_value:
                            extracted_data.append(name_value)
                except Exception as e:
                    QMessageBox.warning(self, "Error", f"Failed to read file '{file_path}': {str(e)}")
        
        # Display the extracted data
        self.display_extracted_data(extracted_data)

    def display_extracted_data(self, extracted_data):
        text_display = ''
        for name in extracted_data:
            text_display += f"Name:{name}\n"
        
        self.custom_card_display.setText(text_display)

    def update_display(self, state, label, line_edit):
        if not hasattr(self, 'checked_inputs'):
            self.checked_inputs = OrderedDict()
        
        value = line_edit.text().strip()
        if state == Qt.Checked:
            if value:  # Only add non-empty inputs
                self.checked_inputs[label] = value
                self.selected_tab_2_inputs_display.append(f"{label} {value}")
        else:
            # Remove the input field from the ordered dictionary if it exists
            if label in self.checked_inputs:
                del self.checked_inputs[label]
                # Update the display by removing the line
                current_text = self.selected_tab_2_inputs_display.toPlainText()
                lines = current_text.split('\n')
                updated_lines = [line for line in lines if not line.startswith(label)]
                self.selected_tab_2_inputs_display.setText('\n'.join(updated_lines))
