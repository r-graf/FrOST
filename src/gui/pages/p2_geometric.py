# src/gui/pages/p2_geometric.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QFormLayout, 
                               QDoubleSpinBox, QSpinBox, QLabel)

class GeometricPage(QWidget):
    def __init__(self):
        super().__init__()
        
        # Hauptlayout der Seite
        layout = QVBoxLayout()
        
        # Überschrift
        layout.addWidget(QLabel("<h2>Schritt 3: Geometrische Verluste</h2>"))
        layout.addWidget(QLabel("Bitte gib die Parameter für die geometrische Berechnung ein."))
        layout.addSpacing(20) # Etwas Abstand

        # Formular-Layout für die Eingaben
        form = QFormLayout()

        # 1. Theta (Strahldivergenz)
        self.input_theta = QDoubleSpinBox()
        self.input_theta.setRange(0, 1000)
        self.input_theta.setDecimals(4)      # Mehr Nachkommastellen für kleine Winkel
        self.input_theta.setSuffix(" rad")   # Oder mrad, je nach deiner Formel
        self.input_theta.setValue(0.001)     # Beispiel-Startwert
        self.input_theta.setSingleStep(0.0001)
        self.input_theta.setMaximumWidth(150)

        # 2. a (Apertur-Radius?)
        self.input_a = QDoubleSpinBox()
        self.input_a.setRange(0, 10)
        self.input_a.setSuffix(" m")
        self.input_a.setValue(0.1)
        self.input_a.setMaximumWidth(150)

        # 3. Jitter Sigma
        self.input_jitter = QDoubleSpinBox()
        self.input_jitter.setRange(0, 1)
        self.input_jitter.setDecimals(6)     # Jitter ist oft sehr klein
        self.input_jitter.setSingleStep(0.000001)
        self.input_jitter.setValue(0.00001)
        self.input_jitter.setMaximumWidth(150)

        # 4. Anzahl Samples (Ganze Zahl -> QSpinBox)
        self.input_samples = QSpinBox()
        self.input_samples.setRange(1, 1_000_000) # Bis 1 Mio erlauben
        self.input_samples.setValue(10000)        # Dein Wunsch-Default
        self.input_samples.setSingleStep(1000)
        self.input_samples.setGroupSeparatorShown(True) # Macht 10.000 statt 10000
        self.input_samples.setMaximumWidth(150)

        # Alles ins Formular packen
        form.addRow("Strahldivergenz (theta):", self.input_theta)
        form.addRow("Apertur-Radius (a):", self.input_a)
        form.addRow("Jitter Sigma:", self.input_jitter)
        form.addRow("Anzahl Samples:", self.input_samples)

        # Formular zum Hauptlayout hinzufügen
        layout.addLayout(form)
        
        # Stretch am Ende schiebt alles schön nach oben
        layout.addStretch()
        
        self.setLayout(layout)

    def get_data(self):
        """Gibt die Werte als Dictionary zurück"""
        return {
            "theta": self.input_theta.value(),
            "a": self.input_a.value(),
            "jitter_sigma": self.input_jitter.value(),
            "n_samples": self.input_samples.value()
        }