import os
os.environ['QT_QPA_PLATFORM'] = 'xcb'
import csv
from fuzzywuzzy import process
from PyQt5.QtCore import QThread, pyqtSignal

class ScriptSearchWorker(QThread):
    resultReady = pyqtSignal(list)

    def __init__(self, search_path, query):
        super().__init__()
        self.search_paths = search_path  # Use a list of paths instead of a single path
        self.query = query

    def run(self):
        # Tokenize the query into keywords and normalize them to lowercase
        keywords = [keyword.strip().lower() for keyword in self.query.split()]
        found_results = []

        for search_path in self.search_paths:
            for o in search_path.rglob('*'):
                if o.is_file():
                    if o.suffix == '.txt':
                        texts = o.read_text()
                        # Normalize the text content to lowercase before searching
                        if all(keyword in texts.lower() for keyword in keywords):
                            found_results.append(texts)
                    elif o.suffix == '.csv':
                        with open(o, 'r', newline='', encoding='utf-8') as csvfile:
                            csvreader = csv.reader(csvfile)
                            for row in csvreader:
                                # Convert the CSV row to lowercase before searching
                                if all(keyword in ','.join(row).lower() for keyword in keywords):
                                    found_results.append(','.join(row))

        self.resultReady.emit(found_results)

    def fuzzy_search(self, text, query):
        return any(process.extractOne(query, [word]) > 80 for word in text.split())
