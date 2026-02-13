# src/gui/main_window.py
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QLabel,
                               QComboBox, QPushButton, QStackedWidget, QMessageBox)
from gui.pages.p1_mode import EbN0InputWidget ,PowerInputWidget, DistanceInputWidget
# Später importieren wir hier deine Logik:
# from core.osc_sim import run_simulation 

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FROST - Free Space Optical Simulation Tool")
        self.resize(500, 400)

        # Zentrales Layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # 1. Auswahl Dropdown
        layout.addWidget(QLabel("<b>Auswahl der Berechnungsmethode für das Eb/N0:</b>"))

        self.mode_selector = QComboBox()
        self.mode_selector.setMaximumWidth(300)
        self.mode_selector.addItems(["Berechnung über Eb/N0", "Berechnung über Leistung", "Berechnung über Distanz"])
        self.mode_selector.currentIndexChanged.connect(self.switch_mask)
        layout.addWidget(self.mode_selector)

        # 2. Stacked Widget (Der Container für die Masken)
        self.stack = QStackedWidget()
        
        self.mask_ebn0 = EbN0InputWidget()
        self.mask_power = PowerInputWidget()
        self.mask_distance = DistanceInputWidget()
        
        self.stack.addWidget(self.mask_ebn0)
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
        current_widget = self.stack.currentWidget()
        
        # Fehlerbehandlung: z.B. ungültige Eingaben
        try:
            # Daten abfragen
            params = current_widget.get_data()
            print(f"Starte Simulation mit Parametern: {params}")
            QMessageBox.information(self, "Info", "Berechnung gestartet... (siehe Konsole)")
        except ValueError as e:
            QMessageBox.warning(self, "Ungültige Eingabe", str(e))
            return
        
        
        # HINWEIS ZUR RECHENLEISTUNG: todo
        # Wenn hier eine schwere Rechnung folgt, friert die GUI ein.
        # Lösung: QThread.
        # Vorerst nur Platzhalter:
