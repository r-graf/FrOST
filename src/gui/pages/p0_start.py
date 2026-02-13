# src/gui/pages/p0_start.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt

class StartPage(QWidget):
    def __init__(self):
        super().__init__()
        
        # Layout erstellen
        layout = QVBoxLayout()
        
        # 1. Oberer Platzhalter (drückt den Inhalt in die Mitte)
        layout.addStretch()

        # 2. Die Überschrift (HTML für Styling nutzen)
        title_label = QLabel("<h1>Willkommen bei FROST</h1>")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        # 3. Der Untertitel / Beschreibungstext
        subtitle_text = (
            "<h3>Free Space Optical Simulation Tool</h3>"
            "<p>Dieses Tool simuliert optische Satellitenkommunikation.</p>"
            "<p>Klicke auf <b>'Weiter'</b>, um die Simulation zu konfigurieren.</p>"
        )
        subtitle_label = QLabel(subtitle_text)
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setWordWrap(True) # Wichtig, falls das Fenster klein ist
        layout.addWidget(subtitle_label)

        # 4. Unterer Platzhalter (drückt den Inhalt in die Mitte)
        layout.addStretch()

        self.setLayout(layout)