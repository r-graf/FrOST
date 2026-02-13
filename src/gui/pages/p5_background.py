from PySide6.QtWidgets import (QWidget, QVBoxLayout, QFormLayout, 
                               QDoubleSpinBox, QComboBox, QLabel)

class BackgroundPage(QWidget):
    def __init__(self):
        super().__init__()
        
        layout = QVBoxLayout()
        
        # Überschrift
        layout.addWidget(QLabel("<h2>Schritt 6: Hintergrundstrahlung</h2>"))
        layout.addWidget(QLabel("Parameter für das Umgebungslicht (Background Noise):"))
        layout.addSpacing(20)

        form = QFormLayout()

        # 1. FOV (Field of View) in mrad
        self.input_fov = QDoubleSpinBox()
        self.input_fov.setRange(0.0, 1000.0)
        self.input_fov.setSuffix(" mrad")
        self.input_fov.setValue(1.0)          # Standard: Enger Winkel
        self.input_fov.setSingleStep(0.1)
        self.input_fov.setMaximumWidth(150)

        # 2. Apertur Durchmesser in cm
        # Hinweis: In Schritt 3 hatten wir Meter, hier cm (wie gewünscht)
        self.input_aperture = QDoubleSpinBox()
        self.input_aperture.setRange(0.0, 500.0)
        self.input_aperture.setSuffix(" cm")
        self.input_aperture.setValue(10.0)    # Standard: 10 cm Teleskop
        self.input_aperture.setMaximumWidth(150)

        # 3. Optischer Filter (Breite) in nm
        self.input_filter = QDoubleSpinBox()
        self.input_filter.setRange(0.0, 1000.0)
        self.input_filter.setSuffix(" nm")
        self.input_filter.setValue(10.0)      # Standard: 10nm Bandpass
        self.input_filter.setMaximumWidth(150)

        # 4. Elektrische Bandbreite in Hz
        # Das sind oft MHz oder GHz -> wir erlauben sehr große Zahlen
        self.input_bandwidth = QDoubleSpinBox()
        self.input_bandwidth.setRange(0.0, 1e12) # Bis 1 THz
        self.input_bandwidth.setSuffix(" Hz")
        self.input_bandwidth.setValue(1e9)       # Standard: 1 GHz
        self.input_bandwidth.setSingleStep(1e6)  # Schritte in MHz
        self.input_bandwidth.setGroupSeparatorShown(True) # Zeigt 1,000,000,000 an
        self.input_bandwidth.setMaximumWidth(200)

        # 5. Himmelsbedingungen (Sky Condition)
        self.input_sky = QComboBox()
        # Key-Value Paare: Was angezeigt wird vs. was wir speichern
        self.sky_options = {
            "Klarer Tag (Sunny)": "sunny",
            "Bewölkt (Cloudy)": "cloudy",
            "Nacht (Night)": "night",
            "Dämmerung (Twilight)": "twilight"
        }
        self.input_sky.addItems(self.sky_options.keys())
        self.input_sky.setCurrentIndex(1) # Default: Bewölkt auswählen
        self.input_sky.setMaximumWidth(200)

        # Ins Formular einfügen
        form.addRow("Field of View (FOV):", self.input_fov)
        form.addRow("Apertur-Durchmesser:", self.input_aperture)
        form.addRow("Optische Filterbreite:", self.input_filter)
        form.addRow("Elektrische Bandbreite:", self.input_bandwidth)
        form.addRow("Himmelsbedingung:", self.input_sky)

        layout.addLayout(form)
        layout.addStretch()
        
        self.setLayout(layout)

    def get_data(self):
        # Den internen Namen für die Sky Condition holen ('cloudy', 'sunny' etc.)
        current_text = self.input_sky.currentText()
        sky_value = self.sky_options[current_text]

        return {
            "fov_mrad": self.input_fov.value(),
            "aperture_diameter_cm": self.input_aperture.value(),
            "optical_filter_width_nm": self.input_filter.value(),
            "electrical_bandwidth_Hz": self.input_bandwidth.value(),
            "sky_condition": sky_value
        }