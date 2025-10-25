import os
os.environ['QT_QPA_PLATFORM'] = 'xcb'
import glob
from pathlib import Path
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (QHBoxLayout, QDialog, 
                             QComboBox, QScrollArea, QInputDialog, 
                             QMessageBox, QListWidgetItem, QApplication, 
                             QWidget, QVBoxLayout, QPushButton, 
                             QLineEdit, QLabel, QTextEdit, QCheckBox, QListWidget)
from app.windows.script_search_worker import ScriptSearchWorker

class ForgeScriptSearchWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.deck_sections = {"Commander": [], "Main": [], "Sideboard": [], "Avatar": [], "Planes": [], "Schemes": [], "Conspiracy": [], "Dungeon": []}
        self.deck = {section: [] for section in self.deck_sections.keys()}
        self.selected_section = ""
        self.selected_cards_display = {}
        self.selectable_cards_list_widget = QListWidget()
        self.selectable_cards_list_widget_remove = None

        self.initUI()
        self.search_path = Path('./app/res/cardsfolder')
        self.output_file = './app/results/search-results.txt'

        # Store references to checkboxes
        self.checkboxes = {}

        self.worker = ScriptSearchWorker(self.search_path, "")
        self.worker.resultReady.connect(self.on_search_results_ready)

        self.results_list = []
        self.displayed_results = []

        # Populate directory selector
        base_directory = './app/custom_created/decks'
        os.makedirs(base_directory, exist_ok=True)
        directories = [d for d in os.listdir(base_directory) if os.path.isdir(os.path.join(base_directory, d))]
        self.directory_selector.addItems(directories)

    def initUI(self):
        # Layout
        main_layout = QHBoxLayout()

        left_layout = QVBoxLayout()
        script_search_deck_creator_label = QLabel("[-- Search for card script(s) in cardsfolder or create a deck --]")
        self.set_font(script_search_deck_creator_label, 'Arial', 11)
        left_layout.addWidget(script_search_deck_creator_label)
        scroll_area = QScrollArea()
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(scroll_content)        
        
        # Initialize scroll_area as an instance variable
        self.scroll_area = scroll_area

        # Connect the scrollbar's valueChanged signal to load_more_results method
        self.scroll_area.verticalScrollBar().valueChanged.connect(self.update_display)
        
        # Search Input
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Enter search query")
        left_layout.addWidget(self.search_input)

        # Connect returnPressed signal to the search function
        self.search_input.returnPressed.connect(self.on_search)

        # Submit Button
        submit_button = QPushButton("Search")
        self.set_font(submit_button, 'Arial', 13)
        submit_button.clicked.connect(self.on_search)
        left_layout.addWidget(submit_button)

        self.checkbox_cardsfolder = QCheckBox("Search in ./app/res/cardsfolder")
        left_layout.addWidget(self.checkbox_cardsfolder)

        self.checkbox_custom_created_cards = QCheckBox("Search in ./app/custom_created/cards")
        left_layout.addWidget(self.checkbox_custom_created_cards)

        # Connect the checkboxes to a slot that updates the directories
        self.checkbox_cardsfolder.stateChanged.connect(self.update_search_directories)
        self.checkbox_custom_created_cards.stateChanged.connect(self.update_search_directories)

        # Display Results
        self.display_results = QTextEdit()
        self.display_results.setReadOnly(True)
        scroll_layout.addWidget(self.display_results)
        left_layout.addWidget(scroll_area)  # Add the scroll area to the layout

        # Add Card Button
        add_card_button = QPushButton("Add Card(s) to Deck")
        self.set_font(add_card_button, 'Arial', 13)
        add_card_button.clicked.connect(self.add_card_to_deck)
        left_layout.addWidget(add_card_button)

        # New button for removing cards
        remove_cards_button = QPushButton("Remove Card(s) from Deck")
        self.set_font(remove_cards_button, 'Arial', 13)
        remove_cards_button.clicked.connect(self.remove_card_from_deck)
        left_layout.addWidget(remove_cards_button)

        # Create Deck Button
        create_deck_button = QPushButton("Create Deck")
        self.set_font(create_deck_button, 'Arial', 13)
        create_deck_button.clicked.connect(self.create_deck)
        left_layout.addWidget(create_deck_button)

        main_layout.addLayout(left_layout)

        right_layout = QVBoxLayout()
        
        selected_cards_label = QLabel("Selected Cards for Deck:")
        right_layout.addWidget(selected_cards_label)

        # Add Directory Selection ComboBox
        self.directory_selector = QComboBox()
        self.directory_selector.addItem("Select a format directory")
        right_layout.addWidget(self.directory_selector)

        self.selected_cards_display = {}
        sections = ["Commander", "Main", "Sideboard", "Avatar", "Planes", "Schemes", "Conspiracy", "Dungeon"]
        for section in sections:
            label = QLabel(f"{section}:")
            right_layout.addWidget(label)
            list_widget = QListWidget()
            right_layout.addWidget(list_widget)
            self.selected_cards_display[section] = list_widget

        # Connect the combo box's currentIndexChanged signal
        self.directory_selector.currentIndexChanged.connect(self.on_directory_selected)

        main_layout.addLayout(right_layout)

        exit_button = QPushButton("Exit")
        self.set_font(exit_button, 'Arial', 13)
        exit_button.clicked.connect(QApplication.quit)
        left_layout.addWidget(exit_button)

        self.setLayout(main_layout)

        # Initialize scroll_area as an instance variable
        self.scroll_area = scroll_area

    def set_font(self, widget, font_name, font_size):
        font = QFont(font_name, font_size)
        widget.setFont(font)

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
        self.worker.search_paths = [Path(directory) for directory in self.search_directories]  # Pass the selected directories to the worker as a list of Path objects
        self.worker.start()

    def on_search_results_ready(self, results):
        if not results:
            self.display_results.append(f"No matches found for any of the keywords: {self.worker.query}. Please try again.")
        else:
            with open(self.output_file, "w", encoding='utf-8') as f:
                f.writelines(result + '\n####\n\n' for result in results)
            with open(self.output_file, 'r', encoding='utf-8') as f:
                self.display_results.setText(f.read())

        # Clear existing checkboxes
        self.checkboxes.clear()

        self.results_list = results
        self.displayed_results = []
        self.load_initial_results()

    def load_initial_results(self):
        self.displayed_results.extend(self.results_list)
        self.update_display()

    def update_display(self):
        self.display_results.clear()
        for result in self.displayed_results:
            self.display_results.append(result)

    def save_results(self):
        # Save the displayed results to a file
        if not os.path.exists(self.output_file):
            print(f"No results to display. Please perform a search first.")
            return
        try:
            with open(self.output_file, 'r', encoding='utf-8') as f:
                content = f.read()
            with open(self.output_file, 'w', encoding='utf-8') as f:
                f.write(content)
            print("Results saved to saved_results.txt.")
        except Exception as e:
            print(f"Failed to save results. {e}")

    def on_directory_selected(self, index):
        if index == 0:
            # Clear the displayed cards when no directory is selected
            for section_list in self.selected_cards_display.values():
                section_list.clear()
            return

        selected_directory = self.directory_selector.currentText()
        base_directory = './app/custom_created/decks'
        full_path = os.path.join(base_directory, selected_directory)

        if not os.path.isdir(full_path):
            QMessageBox.warning(self, "Error", f"Selected directory '{selected_directory}' does not exist.")
            return

        # Show the deck selection dialog
        self.show_deck_selection_dialog(full_path)

    def show_deck_selection_dialog(self, full_path):
        deck_files = glob.glob(os.path.join(full_path, "*.dck"))
        
        if not deck_files:
            QMessageBox.warning(self, "Warning", f"No deck files found in '{full_path}'.")
            return

        # Create a dialog for selecting a deck
        deck_dialog = QDialog(self)
        deck_dialog.setWindowTitle("Select Deck")

        layout = QVBoxLayout()

        list_widget = QListWidget()
        for deck_file in deck_files:
            file_name = os.path.basename(deck_file)
            list_widget.addItem(file_name)

        layout.addWidget(list_widget)

        buttons_layout = QHBoxLayout()

        select_button = QPushButton("Load")
        select_button.clicked.connect(lambda: self.on_deck_selected(list_widget.currentItem().text(), full_path))
        buttons_layout.addWidget(select_button)

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(deck_dialog.reject)
        buttons_layout.addWidget(cancel_button)

        layout.addLayout(buttons_layout)
        deck_dialog.setLayout(layout)

        if deck_dialog.exec_() == QDialog.Accepted:
            # Dialog was accepted, do nothing here since we handle the selection in on_deck_selected
            pass

    def load_deck(self, file_path):
        self.clear_current_deck()  # Ensure all current data is cleared
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                metadata = {}
                current_section = None
                for line in f:
                    line = line.strip()
                    if line.startswith('[') and line.endswith(']'):
                        current_section = line[1:-1]
                        self.deck.setdefault(current_section, [])
                    elif '=' in line:
                        key, value = line.split('=')
                        metadata[key.strip()] = value.strip()
                    elif current_section and line:
                        quantity, card_name = map(str.strip, line.split(maxsplit=1))
                        try:
                            quantity = int(quantity)
                            self.deck[current_section].append((quantity, card_name))
                        except ValueError:
                            print(f"Invalid quantity in file {file_path}: {line}")

            # Display the loaded deck
            for section, cards in self.deck.items():
                if section not in self.selected_cards_display:
                    continue

                for quantity, card_name in cards:
                    self.selected_cards_display[section].addItem(QListWidgetItem(f"{quantity} {card_name}"))
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load deck from '{file_path}'. Error: {str(e)}")

    def clear_current_deck(self):
        for section, section_list in self.selected_cards_display.items():
            if isinstance(section_list, QListWidget):
                section_list.clear()
            else:
                print(f"Section {section} is not a valid QListWidget")

        # Clear the internal deck data
        self.deck.clear()

    def on_deck_selected(self, deck_name, full_path):
        deck_file = os.path.join(full_path, deck_name)
        self.load_deck(deck_file)

    def add_card_to_deck(self):
        # Create a QDialog and set the layout
        card_dialog = QDialog(self)
        card_dialog.setWindowTitle("Add Card to Deck")

        main_layout = QVBoxLayout()

        # Scrollable area for selected cards
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)

        # Add the selectable cards to the list widget
        self.selectable_cards_list_widget = QListWidget()
        with open(self.output_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        for line in lines:
            if line.strip().startswith("Name:"):
                self.selectable_cards_list_widget.addItem(line.strip())

        scroll_layout.addWidget(self.selectable_cards_list_widget)
        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)

        # Deck Section
        deck_section_layout = QVBoxLayout()
        deck_section_label = QLabel("Select Deck Sections:")
        deck_section_layout.addWidget(deck_section_label)

        self.deck_sections = {}
        sections = ["Commander", "Main", "Sideboard", "Avatar", "Planes", "Schemes", "Conspiracy", "Dungeon"]
        for section in sections:
            checkbox = QCheckBox(section)
            deck_section_layout.addWidget(checkbox)
            self.deck_sections[section] = checkbox

        # Dropdown or listbox for deck sections
        section_dropdown = QComboBox()
        for section in self.deck_sections:
            section_dropdown.addItem(section)
        section_dropdown.currentIndexChanged.connect(lambda index: self.on_section_selected(section_dropdown.itemText(index)))
        main_layout.addWidget(section_dropdown)

        # Input field for number
        number_input = QLineEdit()
        number_input.setPlaceholderText("Number of cards to add")
        main_layout.addWidget(number_input)

        # Buttons layout
        buttons_layout = QHBoxLayout()

        add_card_button = QPushButton("Add Card")
        add_card_button.clicked.connect(lambda: self.add_card_to_deck_action(number_input.text(), section_dropdown.currentText()))
        buttons_layout.addWidget(add_card_button)

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(card_dialog.reject)
        buttons_layout.addWidget(cancel_button)

        main_layout.addLayout(buttons_layout)

        card_dialog.setLayout(main_layout)
        if card_dialog.exec_() == QDialog.Accepted:
            # Reset the dialog state before showing it
            for label, checkbox in self.deck_sections.items():
                checkbox.setChecked(False)

    def on_section_selected(self, section):
        self.selected_section = section

    def add_card_to_deck_action(self, number_input, section):
        selected_items = self.selectable_cards_list_widget.selectedItems()
        
        if not selected_items:
            QMessageBox.warning(self, "Warning", "No cards to add.")
            return

        if not section:
            QMessageBox.warning(self, "Warning", "Please select a deck section.")
            return

        for item in selected_items:
            card_text = item.text()
            
            try:
                # Ensure the number input is an integer
                number = int(number_input)
                
                # Extract the card name from the card text
                card_name_parts = card_text.split(":")
                if len(card_name_parts) != 2:
                    raise ValueError(f"Invalid card format: {card_text}")
                
                card_name = card_name_parts[1].strip()
                
                # Check if the card already exists in the deck section
                for i, (existing_quantity, existing_card_name) in enumerate(self.deck[section]):
                    if existing_card_name == card_name:
                        # Increment the quantity of the existing card
                        self.deck[section][i] = (existing_quantity + number, card_name)
                        
                        # Update the display of selected cards in the GUI
                        if section in self.selected_cards_display:
                            current_text = f"{existing_quantity} {card_name}"
                            new_text = f"{existing_quantity + number} {card_name}"
                            for row in range(self.selected_cards_display[section].count()):
                                if self.selected_cards_display[section].item(row).text() == current_text:
                                    self.selected_cards_display[section].item(row).setText(new_text)
                        break
                else:
                    # If the card does not exist, add it as a new entry
                    card_info = (number, card_name)
                    self.deck[section].append(card_info)

                    # Update the display of selected cards in the GUI
                    if section in self.selected_cards_display:
                        self.selected_cards_display[section].addItem(QListWidgetItem(f"{number} {card_name}"))

                QMessageBox.information(self, "Success", f"Card added/updated: {card_name} with quantity {number} to {section}.")
            except ValueError as e:
                QMessageBox.warning(self, "Warning", f"Invalid input: {e}")

    def remove_card_from_deck(self):
        remove_dialog = QDialog(self)
        remove_dialog.setWindowTitle("Remove Card from Deck")

        main_layout = QVBoxLayout()

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)

        self.remove_cards_list_widgets = {}
        sections = ["Commander", "Main", "Sideboard", "Avatar", "Planes", "Schemes", "Conspiracy", "Dungeon"]
        
        for section in sections:
            if section in self.selected_cards_display and self.selected_cards_display[section].count() > 0:
                label = QLabel(f"{section} Cards")
                scroll_layout.addWidget(label)
                
                # Add a QLineEdit for the quantity input
                quantity_input = QLineEdit("1")
                quantity_input.setPlaceholderText("Quantity to Remove")
                scroll_layout.addWidget(quantity_input)

                list_widget = QListWidget()
                for item in range(self.selected_cards_display[section].count()):
                    card_text = self.selected_cards_display[section].item(item).text()
                    list_widget.addItem(card_text)
                
                scroll_layout.addWidget(list_widget)
                self.remove_cards_list_widgets[section] = (list_widget, quantity_input)

        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)

        buttons_layout = QHBoxLayout()

        remove_card_button = QPushButton("Remove Card")
        remove_card_button.clicked.connect(self.remove_selected_card_action)
        buttons_layout.addWidget(remove_card_button)

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(lambda: self.handle_cancel(remove_dialog))
        buttons_layout.addWidget(cancel_button)

        main_layout.addLayout(buttons_layout)

        remove_dialog.setLayout(main_layout)
        if remove_dialog.exec_() == QDialog.Accepted:
            pass

    def handle_cancel(self, dialog):        
        dialog.reject()

    def remove_selected_card_action(self):
        for section, (list_widget, quantity_input) in self.remove_cards_list_widgets.items():
            selected_items = list_widget.selectedItems()
            
            if not selected_items:
                continue

            try:
                # Extract the specified quantity from the QLineEdit
                quantity_to_remove = int(quantity_input.text())
                
                # Ensure the quantity to remove is positive and not greater than the current quantity
                if quantity_to_remove <= 0:
                    QMessageBox.warning(self, "Invalid Quantity", f"Please enter a valid quantity for {section}.")
                    continue
                
                updated_deck = []
                removed_any = False
                for existing_quantity, existing_card_name in self.deck[section]:
                    item_found = False
                    for item in selected_items:
                        card_text = item.text()
                        if existing_card_name == card_text.split(maxsplit=1)[1]:
                            remaining_quantity = int(existing_quantity) - quantity_to_remove
                            
                            if remaining_quantity > 0:
                                updated_deck.append((str(remaining_quantity), existing_card_name))
                                item.setText(f"{remaining_quantity} {existing_card_name}")
                            else:
                                list_widget.takeItem(list_widget.row(item))
                                
                            removed_any = True
                            item_found = True
                            break
                        
                    if not item_found:
                        updated_deck.append((existing_quantity, existing_card_name))

                if removed_any:
                    self.deck[section] = updated_deck

            except Exception as e:
                print(f"Exception occurred: {e}")
                QMessageBox.warning(self, "Warning", f"Failed to remove card: {e}")

        # Update the internal deck data and the display area
        for section, cards in self.deck.items():
            if section in self.selected_cards_display:
                self.selected_cards_display[section].clear()
                for quantity, card_name in cards:
                    self.selected_cards_display[section].addItem(QListWidgetItem(f"{quantity} {card_name}"))

    def create_deck(self):
        deck_name, ok = QInputDialog.getText(self, 'Input Dialog', 'Enter Deck Name:')
        
        if not ok or not deck_name:
            return

        # Define the base directory and list its subdirectories
        base_directory = './app/custom_created/decks'
        os.makedirs(base_directory, exist_ok=True)  # Ensure the base directory exists
        directories = [d for d in os.listdir(base_directory) if os.path.isdir(os.path.join(base_directory, d))]

        # Create a QComboBox with the list of directories
        combo_box = QComboBox()
        combo_box.addItems(directories)
        combo_box.insertItem(0, "Select a directory")  # Add an initial placeholder

        # Open another dialog to get user input including folder selection
        selected_directory, ok = QInputDialog.getItem(self, 'Select Directory', 'Choose the directory:', directories, 0, False)

        if not ok or selected_directory == "":
            return

        # Ensure the selected directory exists
        full_path = os.path.join(base_directory, selected_directory)
        os.makedirs(full_path, exist_ok=True)  # Create the directory if it doesn't exist

        file_path = os.path.join(full_path, f"{deck_name}.dck")

        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                # Write metadata section
                f.write("[metadata]\n")
                f.write(f"Name={deck_name}\n")
                
                for section, cards in self.deck.items():
                    if cards:  # Only write sections that have cards
                        f.write(f"[{section}]\n")
                        for quantity, card_name in cards:
                            f.write(f"{quantity} {card_name}\n")

            QMessageBox.information(self, "Success", f"Deck saved successfully as '{deck_name}.dck'")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to save deck: {str(e)}")
