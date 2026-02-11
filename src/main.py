# src/main.py
import sys
import os

# Pfad anpassen, damit Python das 'src' Paket sauber findet, 
# auch wenn man von woanders startet
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication
from gui.main_window import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())