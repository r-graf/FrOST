from PySide6.QtWidgets import (QWidget, QVBoxLayout, QFormLayout, 
                               QDoubleSpinBox, QLabel)

class AtmospherePage(QWidget):
    def __init__(self):
        super().__init__()
        
        layout = QVBoxLayout()
        
        # Überschrift
        layout.addWidget(QLabel("<h2>Schritt 3: Atmosphärische Verluste</h2>"))
        layout.addWidget(QLabel("Bitte gib die Parameter für die atmosphärische Dämpfung ein."))
        layout.addSpacing(20)

        form = QFormLayout()

        # 1. Sichtweite (Visibility)
        self.input_visibility = QDoubleSpinBox()
        self.input_visibility.setRange(0.1, 500.0) # 100m bis 500km
        self.input_visibility.setSuffix(" km")
        self.input_visibility.setValue(20.0)       # Standard: Klare Sicht
        self.input_visibility.setSingleStep(1.0)
        self.input_visibility.setMaximumWidth(150)

        # 2. Wellenlänge (Wavelength)
        self.input_wavelength = QDoubleSpinBox()
        self.input_wavelength.setRange(100.0, 10000.0) # UV bis Infrarot
        self.input_wavelength.setSuffix(" nm")
        self.input_wavelength.setValue(1550.0)         # Standard: C-Band (Telekom)
        self.input_wavelength.setSingleStep(10.0)
        self.input_wavelength.setMaximumWidth(150)
        
        # Ins Formular einfügen
        form.addRow("Sichtweite (Visibility):", self.input_visibility)
        form.addRow("Wellenlänge (Lambda):", self.input_wavelength)

        layout.addLayout(form)
        layout.addStretch()
        
        self.setLayout(layout)

    def get_data(self):
        return {
            "atmos_visibility_km": self.input_visibility.value(),
            "atmos_wavelength_nm": self.input_wavelength.value()
        }