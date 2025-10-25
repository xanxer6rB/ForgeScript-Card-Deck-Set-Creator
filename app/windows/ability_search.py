import os
import re
from PyQt5.QtWidgets import (QApplication, QScrollArea, QWidget, 
                             QVBoxLayout, QPushButton, QTextEdit, QCheckBox)

# ABILITY PATTERN SEARCH
class AbilitySearchWindow(QWidget):
    def __init__(self):
        super().__init__()
        
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        # Scrollable area for checkboxes
        scroll_area = QScrollArea()
        scroll_content = QWidget()
        #scroll_area.setFixedHeight(200)  # Set a fixed height for the message box
               
        #ability_patterns_label = QLabel("[Search Ability Patterns:]")
        #layout.addWidget(ability_patterns_label)

        scroll_layout = QVBoxLayout(scroll_content)
        scroll_area.setWidgetResizable(True)

        # Checkboxes for patterns
        self.patterns = {
            'K:\\w+': QCheckBox('Pattern 1: K:\\w+'),
            'K:\\w+ \\w+': QCheckBox('Pattern 2: K:\\w+ \\w+'),
            'K:\\w+:\\w+': QCheckBox('Pattern 3: K:\\w+:\\w+'),
            'K:\\w+:\\w+ \\w+': QCheckBox('Pattern 4: K:\\w+:\\w+ \\w+'),
            'K:\\w+ \\w+:\\w+': QCheckBox('Pattern 5: K:\\w+ \\w+:\\w+'),            
            'K:\\w+:\\w+ \\w+': QCheckBox('Pattern 6: K:\\w+:\\w+ \\w+'),
            'K:\\w+:\\w+:\\w+': QCheckBox('Pattern 7: K:\\w+:\\w+:\\w+'),
            'K:\\w+:\\w+:\\w+ \\w+': QCheckBox('Pattern 8: K:\\w+:\\w+:\\w+ \\w+'),
            'K:\\w+ \\w+:\\w+ \\w+': QCheckBox('Pattern 9: K:\\w+ \\w+:\\w+ \\w+'),
            'K:\\w+ \\w+ \\w+ \\w+': QCheckBox('Pattern 10: K:\\w+ \\w+ \\w+ \\w+'),
            "K:\\w+ \\w+[']\\w+ \\w+.": QCheckBox("Pattern 11: K:\\w+ \\w+[']\\w+ \\w+."),
            'K:\\w+:\\w+.\\w+:\\w+ \\w+': QCheckBox('Pattern 12: K:\\w+:\\w+.\\w+:\\w+ \\w+'),
            'K:\\w+:\\w+:\\w+,\\w+,\\w+': QCheckBox('Pattern 13: K:\\w+:\\w+:\\w+,\\w+,\\w+'),
            'K:\\w+:\\w+:\\w+,\\w+,\\w+,\\w+': QCheckBox('Pattern 14: K:\\w+:\\w+:\\w+,\\w+,\\w+,\\w+'),
            'K:\\w+:\\w+:\\w+ \\w+:\\w+[$] \\w+': QCheckBox('Pattern 15: K:\\w+:\\w+:\\w+ \\w+:\\w+[$] \\w+'),
            'K:\\w+:\\w+:::\\w+[$] \\w+[<]\\w+/\\w+[>]': QCheckBox('Pattern 16: K:\\w+:\\w+:::\\w+[$] \\w+[<]\\w+/\\w+[>]'),
            'K:\\w+ \\w+:\\w+[<]\\w+/\\w+[>]:\\w+ {\\w+}.': QCheckBox('Pattern 17: K:\\w+ \\w+:\\w+[<]\\w+/\\w+[>]:\\w+ {\\w+}.'),
            'K:\\w+:\\w+[<]\\w+/\\w+[;]\\w+/\\w+ or \\w+[>]:\\w+': QCheckBox('Pattern 18: K:\\w+:\\w+[<]\\w+/\\w+[;]\\w+/\\w+ or \\w+[>]:\\w+'),
            'K:\\w+ \\w+ \\w+ \\w+ \\w+ \\w+ \\w+ "\\w+ \\w+ \\w+".': QCheckBox('Pattern 19: K:\\w+ \\w+ \\w+ \\w+ \\w+ \\w+ \\w+ "\\w+ \\w+ \\w+".'),
            "K:\\w+ \\w+[']\\w+ \\w+ \\w+ \\w+, \\w+ \\w+ \\w+ \\w+ \\w+ \\w+ \\w+.": QCheckBox("Pattern 20: K:\\w+ \\w+[']\\w+ \\w+ \\w+ \\w+, \\w+ \\w+ \\w+ \\w+ \\w+ \\w+ \\w+."),
            "K:\\w+ \\w+ \\w+ \\w+ \\w+ \\w+ \\w+ \\w+ \\w+[']\\w+ \\w+ \\w+ \\w+ \\w+.": QCheckBox("Pattern 21: K:\\w+ \\w+ \\w+ \\w+ \\w+ \\w+ \\w+ \\w+ \\w+[']\\w+ \\w+ \\w+ \\w+ \\w+."),
            'SVar:\\w+': QCheckBox('Pattern 22: SVar:\\w+'),
            'SVar:\\w+:\\w+': QCheckBox('Pattern 23: SVar:\\w+:\\w+'),
            'SVar:\\w+:\\w+ \\w+': QCheckBox('Pattern 24: SVar:\\w+:\\w+ \\w+'),
            'SVar:\\w+:\\w+.\\w+': QCheckBox('Pattern 25: SVar:\\w+:\\w+.\\w+'),
            'SVar:\\w+:\\w+[$] \\w+': QCheckBox('Pattern 26: SVar:\\w+:\\w+[$] \\w+'),
            'SVar:\\w+:\\w+[$]\\w+ \\w+.\\w+[+]\\w+': QCheckBox('Pattern 27: SVar:\\w+:\\w+[$]\\w+ \\w+.\\w+[+]\\w+'),
            'SVar:\\w+:DB[$] \\w+': QCheckBox('Pattern 28: SVar:\\w+:DB[$] \\w+'),
            'SVar:\\w+:Mode[$] \\w+': QCheckBox('Pattern 29: SVar:\\w+:Mode[$] \\w+'),
            'SVar:\\w+:\\w+[$]\\w+': QCheckBox('Pattern 30: SVar:\\w+:\\w+[$]\\w+'),
            'SVar:\\w+:\\w+[$]\\w+.\\w+.\\w+': QCheckBox('Pattern 31: SVar:\\w+:\\w+[$]\\w+.\\w+.\\w+'),
            'SVar:\\w+:TRUE': QCheckBox('Pattern 32: SVar:\\w+:TRUE'),
            'SVar:\\w+:True': QCheckBox('Pattern 33: SVar:\\w+:True'),
            'SVar:\\w+:FALSE': QCheckBox('Pattern 34: SVar:\\w+:FALSE'),
            'R:\\w+[$] \\w+': QCheckBox('Pattern 35: R:\\w+[$] \\w+'),
            'A:AB[$] \\w+': QCheckBox('Pattern 36: A:AB[$] \\w+'),
            'A:SP[$] \\w+': QCheckBox('Pattern 37: A:SP[$] \\w+'),
            'A:DB[$] \\w+': QCheckBox('Pattern 38: A:DB[$] \\w+'),
            'T:Mode[$] \\w+': QCheckBox('Pattern 39: T:Mode[$] \\w+'),
            'S:Mode[$] \\w+': QCheckBox('Pattern 40: S:Mode[$] \\w+'),
            'SubAbility[$] \\w+': QCheckBox('Pattern 41: SubAbility[$] \\w+'),
            'AlternateMode:\\w+': QCheckBox('Pattern 42: AlternateMode:\\w+'),
            'MeldPair:\\w+, \\w+ \\w+ \\w+': QCheckBox('Pattern 43: MeldPair:\\w+, \\w+ \\w+ \\w+'),
            'AILogic[$] \\w+': QCheckBox('Pattern 44: AILogic[$] \\w+'),
            'DeckHints:\\w+': QCheckBox('Pattern 45: DeckHints:\\w+'),
            'DeckHints:\\w+[$]\\w+': QCheckBox('Pattern 46: DeckHints:\\w+[$]\\w+'),
            '\\w+:\\w+[$]\\w+': QCheckBox('Patttern 47: \\w:\\w+[$]\\w+'),
            '\\w+:\\w+[$] \\w+': QCheckBox('Patttern 48: \\w:\\w+[$] \\w+'),
            '\\w+[$]\\w+': QCheckBox('Patttern 49: \\w+[$]\\w+'),
            '\\w+[$] \\w+': QCheckBox('Patttern 50: \\w+[$] \\w+')                                                
        }
        
        for pattern, checkbox in self.patterns.items():
            scroll_layout.addWidget(checkbox)
        
        scroll_area.setWidget(scroll_content)
        layout.addWidget(scroll_area)
        
        # Display area for results
        self.results_display = QTextEdit()
        self.results_display.setReadOnly(True)
        layout.addWidget(self.results_display)
        
        # Search button
        search_button = QPushButton("Search")
        search_button.clicked.connect(self.perform_search_and_display)
        layout.addWidget(search_button)

        # Save button
        save_button = QPushButton('Save Results')
        save_button.clicked.connect(self.save_results)
        layout.addWidget(save_button)

        # Go Back to Main Menu button
#        back_button = QPushButton("Back to Main Menu")
#        back_button.clicked.connect(lambda: self.parent().setCentralWidget(MainMenu()))
#        layout.addWidget(back_button)

        self.setLayout(layout)
    
    def perform_search_and_display(self):
        search_directory = './app/res/cardsfolder'
        
        selected_patterns = [pattern for pattern, checkbox in self.patterns.items() if checkbox.isChecked()]
        
        unique_words = set()
        
        # Walk through all directories and files in the specified directory
        for root, _, files in os.walk(search_directory):
            for file in files:
                if file.endswith('.txt'):
                    file_path = os.path.join(root, file)
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                        # Find all occurrences of the selected patterns followed by a word
                        for pattern in selected_patterns:
                            matches = re.findall(pattern, content)
                            
                            # Add the matched words to the set of unique words
                            if matches:
                                unique_words.update(matches)
        
        self.results_display.clear()
        self.results_display.append(f"Number of unique words found: {len(unique_words)}\n")
        for word in sorted(unique_words):
            self.results_display.append(word)

    def save_results(self):
        output_file_path = './app/results/ability_results.txt'
        
        with open(output_file_path, 'w', encoding='utf-8') as f:
            for line in self.results_display.toPlainText().split('\n'):
                if line.strip():
                    f.write(f"{line}\n")
        
        print(f"Results have been saved to {output_file_path}")

    def back_to_main_menu(self):
        self.parent().show()
        self.hide()

class MainApplication(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        start_search_button = QPushButton('Start Search')
        start_search_button.clicked.connect(self.show_search_window)

        display_results_button = QPushButton('Display Results')
        display_results_button.clicked.connect(self.display_results)

        exit_button = QPushButton('Exit Program')
        exit_button.clicked.connect(QApplication.instance().quit)

        layout.addWidget(start_search_button)
        layout.addWidget(display_results_button)
        layout.addWidget(exit_button)

        self.setLayout(layout)
    
    def show_search_window(self):
        self.search_window = AbilitySearchWindow()
        self.search_window.parent = self
        self.search_window.show()
        self.hide()

    def display_results(self):
        output_file_path = './app/results/ability_results.txt'
        
        try:
            with open(output_file_path, 'r', encoding='utf-8') as f:
                print("\nSearch Results:")
                for line in f:
                    word = line.strip()
                    if word:
                        print(word)
        except FileNotFoundError:
            print("No results found. Please perform a search first.")