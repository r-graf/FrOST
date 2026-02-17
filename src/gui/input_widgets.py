# src/gui/input_widgets.py
from PySide6.QtWidgets import QWidget, QFormLayout, QSpinBox, QDoubleSpinBox, QHBoxLayout, QComboBox, QLabel

class EbN0InputWidget(QWidget):
    """Maske 0: Berechnung über Eb/N0"""
    def __init__(self):
        super().__init__()
        form_layout = QFormLayout()
        
        self.input_ebn0_min = QDoubleSpinBox()
        self.input_ebn0_min.setRange(-1, 30)
        self.input_ebn0_min.setValue(0)
        self.input_ebn0_min.setSuffix(" dB")

        self.input_ebn0_max = QDoubleSpinBox()
        self.input_ebn0_max.setRange(-1, 30)
        self.input_ebn0_max.setValue(12)
        self.input_ebn0_max.setSuffix(" dB")

        self.input_steps = QSpinBox()
        self.input_steps.setRange(1, 1000)
        self.input_steps.setSuffix(" Schritte")
        self.input_steps.setValue(5)
        
        form_layout.addRow("min. Eb/N0:", self.input_ebn0_min)
        form_layout.addRow("max. Eb/N0:", self.input_ebn0_max)
        form_layout.addRow("Simulationsauflösung:", self.input_steps)
        
        main_layout = QHBoxLayout()
        main_layout.addLayout(form_layout)
        main_layout.addStretch() # Damit die Formulare links bleiben
        
        self.setLayout(main_layout)

    def get_data(self):
        if self.input_ebn0_min.value() >= self.input_ebn0_max.value():
            raise ValueError("Eb/N0 min muss kleiner sein als Eb/N0 max.")

        return {
            "mode": "ebn0",
            "ebn0_min": self.input_ebn0_min.value(),
            "ebn0_max": self.input_ebn0_max.value(),
            "steps": self.input_steps.value()
        }

class PowerInputWidget(QWidget):
    """Maske 1: Berechnung über Leistung"""
    def __init__(self):
        super().__init__()
        form_layout = QFormLayout()
        
        self.input_power = QDoubleSpinBox()
        self.input_power.setRange(-200, 10000)
        self.input_power.setValue(10)
        
        self.unit_selector = QComboBox()
        self.unit_selector.addItems(["W", "dBm", "dBW"])
        self.unit_selector.setMaximumWidth(80)

        power_layout = QHBoxLayout()
        power_layout.addWidget(self.input_power)
        power_layout.addWidget(self.unit_selector)
        power_layout.addStretch()

        self.input_distance_min = QDoubleSpinBox()
        self.input_distance_min.setRange(0, 100000)
        self.input_distance_min.setSuffix(" km")
        self.input_distance_min.setValue(1)


        self.input_distance_max = QDoubleSpinBox()
        self.input_distance_max.setRange(0, 100000)
        self.input_distance_max.setSuffix(" km")
        self.input_distance_max.setValue(100)

        self.input_steps = QSpinBox()
        self.input_steps.setRange(1, 1000)
        self.input_steps.setSuffix(" Schritte")
        self.input_steps.setValue(5)

        form_layout.addRow(QLabel("Angabe der zu untersuchenden Leistung. \n" \
                                  "Für diese Leistung wird das Eb/N0 korrespondierend\n" \
                                  "über einen Distanzbereich berechnet."))
        form_layout.addRow("Sendeleistung (P_tx):", power_layout)
        form_layout.addRow("Startdistanz:", self.input_distance_min)
        form_layout.addRow("Enddistanz:", self.input_distance_max)
        form_layout.addRow("Simulationsauflösung:", self.input_steps)

        main_layout = QHBoxLayout()
        main_layout.addLayout(form_layout)
        main_layout.addStretch() # Damit die Formulare links bleiben
        
        self.setLayout(main_layout)

    def get_data(self):
        """
        Gibt die Leistungen in Watt zurück, unabhängig von der gewählten Einheit.
        """
        raw_value = self.input_power.value()
        unit = self.unit_selector.currentText()

        # Ungültige Eingaben abfangen
        if raw_value < 0 and unit == "W":
            raise ValueError("Lineare Leistung [W] muss positiv sein.")
        if self.input_distance_min.value() > self.input_distance_max.value():
            raise ValueError("Startdistanz muss kleiner sein als Enddistanz.")
        if self.input_distance_min.value() == self.input_distance_max.value():
            raise ValueError("Startdistanz und Enddistanz dürfen nicht gleich sein.")
        if self.input_distance_min.value() < 0 or self.input_distance_max.value() < 0:
            raise ValueError("Distanzen müssen positiv sein. Wie zum Fick hast du das hinbekommen?")
        if self.input_steps.value() <= 0:
            raise ValueError("Anzahl der Segmente muss größer als 0 sein. Wie zum Fick hast du das hinbekommen?")

        return {
            "mode": "power",
            "geo_p_tx_W": convert_to_watt(raw_value, unit),
            "geo_min_dist_km": self.input_distance_min.value(),
            "geo_max_dist_km": self.input_distance_max.value(),
            "geo_steps": self.input_steps.value()
        }

class DistanceInputWidget(QWidget):
    """Maske 2: Berechnung über Distanz"""
    def __init__(self):
        super().__init__()
        form_layout = QFormLayout()
        
        self.input_distance = QDoubleSpinBox()
        self.input_distance.setRange(0, 100000)
        self.input_distance.setSuffix(" km")
        self.input_distance.setValue(36000) # Default GEO

        self.input_start_power = QDoubleSpinBox()
        self.input_start_power.setRange(-20, 10000)
        self.input_start_power.setValue(10)

        self.input_end_power = QDoubleSpinBox()
        self.input_end_power.setRange(-20, 10000)
        self.input_end_power.setValue(100)
        
        self.unit_selector = QComboBox()
        self.unit_selector.addItems(["W", "dBm", "dBW"])
        self.unit_selector.setMaximumWidth(80)

        start_power_layout = QHBoxLayout()
        start_power_layout.addWidget(self.input_start_power)
        start_power_layout.addWidget(self.unit_selector)
        start_power_layout.addStretch()

        end_power_layout = QHBoxLayout()
        end_power_layout.addWidget(self.input_end_power)
        end_power_layout.addWidget(self.unit_selector)
        end_power_layout.addStretch()

        self.input_steps = QSpinBox()
        self.input_steps.setRange(1, 1000)
        self.input_steps.setSuffix(" Schritte")
        self.input_steps.setValue(5)

        form_layout.addRow("Distanz:", self.input_distance)
        form_layout.addRow("Minimale Leistung:", start_power_layout)
        form_layout.addRow("Maximale Leistung:", end_power_layout)
        form_layout.addRow("Simulationsauflösung:", self.input_steps)

        main_layout = QHBoxLayout()
        main_layout.addLayout(form_layout)
        main_layout.addStretch() # Damit die Formulare links bleiben

        self.setLayout(main_layout)

    def get_data(self):
        """
        Gibt die Leistungen in Watt zurück, unabhängig von der gewählten Einheit.
        """
        if self.input_start_power.value() >= self.input_end_power.value():
            raise ValueError("Minimale Leistung muss kleiner sein als maximale Leistung.")
        if self.input_start_power.value() < 0 and self.unit_selector.currentText() == "W":
            raise ValueError("Lineare Leistung [W] muss positiv sein.")
        if self.input_distance.value() < 0:
            raise ValueError("Distanz muss positiv sein. Wie zum Fick hast du das hinbekommen?")

        return {
            "mode": "distance",
            "distance_km": self.input_distance.value(),
            "start_power_W": convert_to_watt(self.input_start_power.value(), self.unit_selector.currentText()),
            "end_power_W": convert_to_watt(self.input_end_power.value(), self.unit_selector.currentText()),
            "steps": self.input_steps.value()
        }

def convert_to_watt(value, unit):
    if unit == "dBm":
        return 10 ** ((value - 30) / 10)
    elif unit == "dBW":
        return 10 ** (value / 10)
    else:  # unit == "W"
        return value