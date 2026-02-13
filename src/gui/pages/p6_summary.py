from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QTextEdit)

class SummaryPage(QWidget):
    def __init__(self):
        super().__init__()
        
        layout = QVBoxLayout()
        
        # Überschrift
        layout.addWidget(QLabel("<h2>Zusammenfassung</h2>"))
        layout.addWidget(QLabel("Bitte überprüfe deine Parameter vor dem Start:"))
        
        # Das Textfeld für die Daten (Read-Only, damit man nichts löschen kann)
        self.text_display = QTextEdit()
        self.text_display.setReadOnly(True)
        layout.addWidget(self.text_display)
        
        self.setLayout(layout)

    def update_summary(self, data):
        """
        Diese Funktion wird vom MainWindow aufgerufen, bevor diese Seite angezeigt wird.
        Sie bekommt das Dictionary mit ALLEN gesammelten Daten.
        """
        # 1. Text leeren
        self.text_display.clear()
        
        # 2. HTML-Text zusammenbauen für schöne Formatierung
        html_text = "<h3>Simulations-Parameter:</h3><ul>"
        
        # Durch das Dictionary iterieren
        for key, value in data.items():
            # Wir machen die Keys etwas lesbarer (optional)
            readable_key = key.replace("_", " ").capitalize()
            html_text += f"<li><b>{readable_key}:</b> {value}</li>"
            
        html_text += "</ul>"
        
        # 3. Text setzen
        self.text_display.setHtml(html_text)