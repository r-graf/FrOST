# src/gui/main_window.py
import sys
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                               QPushButton, QStackedWidget, QMessageBox)

# Importiere deine Seiten (wir erstellen die Dateien gleich)
from gui.pages.p0_start import StartPage
from gui.pages.p1_mode import ModePage
from gui.pages.p2_geometric import GeometricPage
from gui.pages.p3_atmos import AtmospherePage
from gui.pages.p4_scinti import ScintillationPage
from gui.pages.p5_background import BackgroundPage
from gui.pages.p6_summary import SummaryPage

from core.fso_channel import calculate_geometric_and_pointing_loss

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FROST - Free Space Optical Simulation Tool")
        self.resize(800,600)

        # Zentrales Widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # --- 1. Seitencontainer ---
        self.stack = QStackedWidget()
        
        # Instanzen der Seiten
        self.page_start = StartPage()
        self.page_mode = ModePage()
        self.page_geo = GeometricPage()
        self.page_atmos = AtmospherePage()
        self.page_scinti = ScintillationPage()
        self.page_bckgrnd = BackgroundPage()
        self.page_summary = SummaryPage()

        # Seiten zum Stack hinzufügen
        self.stack.addWidget(self.page_start)   # Index 0
        self.stack.addWidget(self.page_mode)    # Index 1
        self.stack.addWidget(self.page_geo)     # Index 2
        self.stack.addWidget(self.page_atmos)   # Index 3
        self.stack.addWidget(self.page_scinti)  # Index 4
        self.stack.addWidget(self.page_bckgrnd) # Index 5
        self.stack.addWidget(self.page_summary) # Index 6

        main_layout.addWidget(self.stack)

        # --- 2. Navigationsleiste ---
        nav_layout = QHBoxLayout()
        
        self.btn_back = QPushButton("< Zurück")
        self.btn_back.clicked.connect(self.go_back)
        self.btn_back.setEnabled(False) # Am Anfang inaktiv
        
        self.btn_next = QPushButton("Weiter >")
        self.btn_next.clicked.connect(self.go_next)
        
        nav_layout.addWidget(self.btn_back)
        nav_layout.addStretch() # Schiebt Buttons auseinander (optional)
        nav_layout.addWidget(self.btn_next)
        
        main_layout.addLayout(nav_layout)

        # Dictionary um ALLE Daten der Simulation zu sammeln
        self.simulation_data = {}        

    def go_next(self):
            """Geht eine Seite weiter und speichert Daten der aktuellen Seite"""
            current_index = self.stack.currentIndex()
            current_page = self.stack.currentWidget()

            # 1. Daten der aktuellen Seite sichern (Validierung!)
            if hasattr(current_page, "get_data"):
                try:
                    page_data = current_page.get_data()
                    # Speichere die Daten im zentralen Dictionary unter dem Namen der Seite
                    # oder flach, je nach Geschmack. Hier: Update ins Haupt-Dict.
                    self.simulation_data.update(page_data)
                    print(f"Update calculation parameters: {self.simulation_data}") 
                except ValueError as e:
                    QMessageBox.warning(self, "Fehler", str(e))
                    return # Nicht weitergehen bei Fehler!

            # 2. Spezialfall: Sind wir auf der vorletzten Seite?
            # Dann muss der Button vielleicht "Start" heißen oder wir füllen die Summary Page
            if current_index + 1 == self.stack.count() - 1:
                # Wir gehen jetzt zur Summary Page -> Daten übergeben!
                self.page_summary.update_summary(self.simulation_data)
                self.btn_next.setText("Berechnung starten")
            elif current_index == self.stack.count() - 1:
                # Wir sind auf der letzten Seite und haben geklickt -> START
                self.start_simulation()
                return

            # 3. Seite wechseln
            if current_index < self.stack.count() - 1:
                self.stack.setCurrentIndex(current_index + 1)
                self.update_buttons()

    def go_back(self):
            current_index = self.stack.currentIndex()
            if current_index > 0:
                self.stack.setCurrentIndex(current_index - 1)
                self.update_buttons()

    def update_buttons(self):
            idx = self.stack.currentIndex()
            # Zurück-Button Logik
            self.btn_back.setEnabled(idx > 0)
            
            # Weiter-Button Text Logik
            if idx == self.stack.count() - 1:
                self.btn_next.setText("Berechnung starten")
            else:
                self.btn_next.setText("Weiter >")

    def start_simulation(self):
            print("--- START CALCULATION Eb/N0 ---")
            print("All calculation parameters:", self.simulation_data)
            QMessageBox.information(self, "Erfolg                    ",
                                          "Berechung wurde gestartet!")
            
            if self.simulation_data.get("mode") == "distance":
                print("Mode: ", self.simulation_data.get("mode"))
                print("Distance: ", self.simulation_data.get("distance_km"))