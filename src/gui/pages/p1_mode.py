from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QComboBox, 
                               QStackedWidget)
from gui.input_widgets import EbN0InputWidget, PowerInputWidget, DistanceInputWidget

class ModePage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("<h2>Schritt 1: Berechnungsmethode</h2>"))
        
        # Dropdown
        self.mode_selector = QComboBox()
        self.mode_selector.addItems(["Berechnung über Eb/N0", "Berechnung über Leistung", "Berechnung über Distanz"])
        self.mode_selector.currentIndexChanged.connect(self.switch_mask)
        layout.addWidget(self.mode_selector)

        # Stack für die Masken
        self.stack = QStackedWidget()
        self.mask_ebn0 = EbN0InputWidget()
        self.mask_power = PowerInputWidget()
        self.mask_distance = DistanceInputWidget()
        
        self.stack.addWidget(self.mask_ebn0)
        self.stack.addWidget(self.mask_power)
        self.stack.addWidget(self.mask_distance)
        
        layout.addWidget(self.stack)
        self.setLayout(layout)

    def switch_mask(self, index):
        self.stack.setCurrentIndex(index)

    def get_data(self):
        # Leitet die Anfrage an die gerade sichtbare Maske weiter
        return self.stack.currentWidget().get_data()