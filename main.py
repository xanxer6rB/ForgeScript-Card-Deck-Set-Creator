import os
os.environ['QT_QPA_PLATFORM'] = 'xcb'
import sys
from PyQt5.QtWidgets import QTabWidget, QApplication, QMainWindow
from app.windows.backup_update_cardsfolder import UpdateCardsfolderWindow
from app.windows.custom_card_creator import CustomCardCreatorWindow
from app.windows.script_search_deckbuilder import ForgeScriptSearchWindow
#from app.windows.ability_search import AbilitySearchWindow

# WINDOW NAMES AND TABS
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("[-- Forge Script Search and Deck Builder --]")

        app.setStyleSheet("""
            QWidget {
                background-color: #1E1E1E;
                color: #E1D442;
                font-family: Arial, sans-serif;
            }
            QLabel {
                font-size: 14px;
                color: #00D3FB;
            }
            QLineEdit, QTextEdit, QListWidget {
                background-color: #2E2E2E;
                color: #E1D442;
                border: 1px solid #505050;
                padding: 5px;
                border-radius: 5px;
            }
            QPushButton {
                background-color: #4A4A4A;
                color: #00CFFB;
                border: none;
                padding: 10px;
                font-size: 16px;
                border-radius: 5px;
            }
            QPushButton, QCheckBox:hover {
                background-color: #3B3B3B;
            }
        """)

        # Create a tab widget
        tabs = QTabWidget()

        # Create instances of the search windows
        custom_card_creator_window = CustomCardCreatorWindow()        
        script_search_window = ForgeScriptSearchWindow()
#        ability_search = AbilitySearchWindow()
        update_cardsfolder_backup = UpdateCardsfolderWindow()
        tabs.addTab(custom_card_creator_window, "Custom Card and Set Creator")
        tabs.addTab(script_search_window, "Script Search and Deck Builder")
#        tabs.addTab(ability_search, "Ability Pattern Search")
        tabs.addTab(update_cardsfolder_backup, "Update Cardsfolder or Create a Backup")
        self.setCentralWidget(tabs)

# APP MAIN WINDOW
class ForgeBuilderApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("[-- Forge Script Search and Deck Builder App --]")
        self.setGeometry(100, 100, 800, 600)
#        self.setGeometry(100, 100, 1200, 800)        
        self.setCentralWidget(MainWindow())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = ForgeBuilderApp()
    ex.show()
    sys.exit(app.exec_())