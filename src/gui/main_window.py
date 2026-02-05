# src/gui/main_window.py
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                               QComboBox, QPushButton, QStackedWidget, QMessageBox)
from gui.input_widgets import PowerInputWidget, DistanceInputWidget
# Später importieren wir hier deine Logik:
# from core.osc_sim import run_simulation 

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SatCom Sim - Eb/N0 Calculator")
        self.resize(400, 300)

        # Zentrales Layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # 1. Auswahl Dropdown
        self.mode_selector = QComboBox()
        self.mode_selector.addItems(["Berechnung über Leistung", "Berechnung über Distanz"])
        self.mode_selector.currentIndexChanged.connect(self.switch_mask)
        layout.addWidget(self.mode_selector)

        # 2. Stacked Widget (Der Container für die Masken)
        self.stack = QStackedWidget()
        
        self.mask_power = PowerInputWidget()
        self.mask_distance = DistanceInputWidget()
        
        self.stack.addWidget(self.mask_power)    # Index 0
        self.stack.addWidget(self.mask_distance) # Index 1
        
        layout.addWidget(self.stack)

        # 3. Start Button
        self.btn_start = QPushButton("Simulation starten")
        self.btn_start.clicked.connect(self.start_simulation)
        layout.addWidget(self.btn_start)

    def switch_mask(self, index):
        """Wechselt die angezeigte Maske im Stack basierend auf Dropdown"""
        self.stack.setCurrentIndex(index)

    def start_simulation(self):
        """Holt Daten aus der aktiven Maske und startet Berechnung"""
        
        # Welche Maske ist gerade aktiv?
        current_index = self.stack.currentIndex()
        current_widget = self.stack.currentWidget()
        
        # Daten abfragen
        params = current_widget.get_data()
        
        print(f"Starte Simulation mit Parametern: {params}")
        
        # HINWEIS ZUR RECHENLEISTUNG:
        # Wenn hier eine schwere Rechnung folgt, friert die GUI ein.
        # Lösung: QThread (dazu komme ich gleich).
        # Vorerst nur Platzhalter:
        QMessageBox.information(self, "Info", "Berechnung gestartet... (siehe Konsole)")