import webbrowser
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QLabel
from PySide6.QtCore import Slot

class BrowserWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # URL input section
        url_layout = QHBoxLayout()
        
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Enter URL")
        url_layout.addWidget(self.url_input)

        go_button = QPushButton('Ir')
        go_button.clicked.connect(self.load_url)
        url_layout.addWidget(go_button)

        layout.addLayout(url_layout)

        # Info label
        self.info_label = QLabel('Haga clic en "Ir" para abrir en el navegador predeterminado')
        layout.addWidget(self.info_label)

    @Slot()
    def load_url(self):
        url = self.url_input.text()
        if not url.startswith(('http://', 'https://')):
            url = 'http://' + url

        try:
            webbrowser.open(url)
            self.info_label.setText(f'Abriendo: {url}')
        except Exception as e:
            self.info_label.setText(f'Error al abrir URL: {str(e)}')