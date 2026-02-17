from PySide6.QtWidgets import (QWidget, QVBoxLayout, QFormLayout, 
                               QDoubleSpinBox, QLabel)

class ScintillationPage(QWidget):
    def __init__(self):
        super().__init__()
        
        layout = QVBoxLayout()
        
        # Überschrift
        layout.addWidget(QLabel("<h2>Schritt 5: Szintillation (Turbulenz)</h2>"))
        layout.addWidget(QLabel("Parameter für das Szintillations-Modell (z.B. Rytov):"))
        layout.addSpacing(20)

        form = QFormLayout()

        # 1. Cn2 (Brechungsindex-Strukturparameter)
        # Werte sind extrem klein, z.B. 1e-14. Daher viele Dezimalstellen nötig.
        self.input_cn2 = QDoubleSpinBox()
        self.input_cn2.setDecimals(16)        # Bis 10^-16 anzeigen
        self.input_cn2.setRange(0, 1e-10)     # Obergrenze
        self.input_cn2.setSingleStep(1e-15)   # Kleine Schritte beim Klicken
        self.input_cn2.setValue(1.7e-14)      # Typischer Wert (moderat)
        self.input_cn2.setSuffix(" m^(-2/3)")
        self.input_cn2.setMaximumWidth(200)   # Etwas breiter für die vielen Nullen
        self.input_cn2.setToolTip("Refractive Index Structure Parameter (typisch 10^-17 bis 10^-13)")

        # 2. L_m (Pfadlänge durch das Medium)
        self.input_L = QDoubleSpinBox()
        self.input_L.setSuffix(" m")
        self.input_L.setRange(0, 1e6)         # Bis 1000 km
        self.input_L.setValue(20000.0)        # Standard: 20 km (Atmosphärendicke)
        self.input_L.setMaximumWidth(200)

        # 3. Wavelength (nm)
        self.input_wavelength = QDoubleSpinBox()
        self.input_wavelength.setDecimals(1)
        self.input_wavelength.setRange(100, 10000) # UV bis IR
        self.input_wavelength.setSuffix(" nm")
        self.input_wavelength.setValue(1550)
        self.input_wavelength.setSingleStep(10)
        self.input_wavelength.setMaximumWidth(150)

        # Formular befüllen
        form.addRow("Cn² (Strukturparameter):", self.input_cn2)
        form.addRow("Pfadlänge (L_m):", self.input_L)
        form.addRow("Wellenlänge (Lambda):", self.input_wavelength)

        layout.addLayout(form)
        layout.addStretch()
        
        self.setLayout(layout)

    def get_data(self):
        return {
            "scinti_cn2": self.input_cn2.value(),
            "scinti_L_m": self.input_L.value(),
            "scinti_wavelength_nm": self.input_wavelength.value()
        }