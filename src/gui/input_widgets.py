# src/gui/input_widgets.py
from PySide6.QtWidgets import QWidget, QFormLayout, QDoubleSpinBox, QLabel

class PowerInputWidget(QWidget):
    """Maske 1: Berechnung über Leistung"""
    def __init__(self):
        super().__init__()
        layout = QFormLayout()
        
        self.input_power = QDoubleSpinBox()
        self.input_power.setRange(0, 1000)
        self.input_power.setSuffix(" W")
        
        self.input_losses = QDoubleSpinBox()
        self.input_losses.setSuffix(" dB")
        
        layout.addRow("Sendeleistung (P_tx):", self.input_power)
        layout.addRow("Systemverluste:", self.input_losses)
        self.setLayout(layout)

    def get_data(self):
        return {
            "mode": "power",
            "p_tx": self.input_power.value(),
            "losses": self.input_losses.value()
        }

class DistanceInputWidget(QWidget):
    """Maske 2: Berechnung über Distanz"""
    def __init__(self):
        super().__init__()
        layout = QFormLayout()
        
        self.input_distance = QDoubleSpinBox()
        self.input_distance.setRange(0, 100000)
        self.input_distance.setSuffix(" km")
        self.input_distance.setValue(36000) # Default GEO
        
        layout.addRow("Distanz:", self.input_distance)
        self.setLayout(layout)

    def get_data(self):
        return {
            "mode": "distance",
            "distance": self.input_distance.value()
        }