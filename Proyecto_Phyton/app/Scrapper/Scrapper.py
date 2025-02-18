import threading
import requests
from bs4 import BeautifulSoup
import sqlite3
import time
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                              QLabel, QLineEdit, QTableWidget, QTableWidgetItem, QFrame)
from PySide6.QtCore import Qt, Signal, Slot, QThread, QTimer

# Database configuration
DB_PATH = 'scrapper.db'

class DatabaseManager:
    @staticmethod
    def conectar_bd():
        try:
            conexion = sqlite3.connect(DB_PATH)
            return conexion
        except sqlite3.Error as e:
            print(f"Error al conectar a la base de datos: {e}")
            return None

    @staticmethod
    def inicializar_bd():
        conexion = DatabaseManager.conectar_bd()
        if conexion:
            try:
                cursor = conexion.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS monitoreo_web (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        titulo TEXT,
                        contenido TEXT,
                        url TEXT,
                        fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                conexion.commit()
            except sqlite3.Error as e:
                print(f"Error al inicializar la base de datos: {e}")
            finally:
                cursor.close()
                conexion.close()

    @staticmethod
    def guardar_datos(titulo, contenido, url):
        conexion = DatabaseManager.conectar_bd()
        if conexion:
            try:
                cursor = conexion.cursor()
                query = """
                    INSERT INTO monitoreo_web (titulo, contenido, url)
                    VALUES (?, ?, ?)
                """
                cursor.execute(query, (titulo, contenido, url))
                conexion.commit()
                return True
            except sqlite3.Error as e:
                print(f"Error al guardar datos: {e}")
                return False
            finally:
                cursor.close()
                conexion.close()
        return False

class ScraperThread(QThread):
    status_updated = Signal(str)
    finished = Signal()

    def __init__(self, url):
        super().__init__()
        self.url = url
        self.running = False

    def run(self):
        self.running = True
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(self.url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            titulo = soup.title.string if soup.title else 'Sin título'
            
            contenido = ''
            for parrafo in soup.find_all(['p', 'article', 'div']):
                if parrafo.text.strip():
                    contenido += parrafo.text.strip() + '\n'
            contenido = contenido[:1000]

            if DatabaseManager.guardar_datos(titulo, contenido, self.url):
                self.status_updated.emit(f"Datos guardados: {titulo}")
            else:
                self.status_updated.emit("Error al guardar en la base de datos")
        except Exception as e:
            self.status_updated.emit(f"Error: {str(e)}")
        finally:
            self.running = False
            self.finished.emit()

class ScraperApp(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.scraper_thread = None
        self.setup_update_timer()
        DatabaseManager.inicializar_bd()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Results display
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(4)
        self.results_table.setHorizontalHeaderLabels(["Título", "Contenido", "URL", "Fecha"])
        self.results_table.setFixedSize(800, 600)  # Establece un tamaño fijo más ancho y más alto
        layout.addWidget(self.results_table)

        # URL input section
        input_frame = QFrame()
        input_layout = QHBoxLayout(input_frame)
        
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Enter URL to scrape")
        input_layout.addWidget(self.url_input)

        self.start_button = QPushButton("Start Scraping")
        self.start_button.clicked.connect(self.start_scraping)
        input_layout.addWidget(self.start_button)

        layout.addWidget(input_frame)

        # Status label
        self.status_label = QLabel("Ready")
        layout.addWidget(self.status_label)

    def setup_update_timer(self):
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_results)
        self.update_timer.start(5000)  # Update every 5 seconds

    @Slot()
    def start_scraping(self):
        url = self.url_input.text().strip()
        if not url:
            self.status_label.setText("Please enter a URL")
            return

        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url

        if not self.scraper_thread or not self.scraper_thread.running:
            self.scraper_thread = ScraperThread(url)
            self.scraper_thread.status_updated.connect(self.update_status)
            self.scraper_thread.finished.connect(self.scraping_finished)
            self.scraper_thread.start()
            self.start_button.setEnabled(False)
            self.status_label.setText(f"Scraping {url}...")

    @Slot(str)
    def update_status(self, message):
        self.status_label.setText(message)

    @Slot()
    def scraping_finished(self):
        self.start_button.setEnabled(True)
        self.update_results()

    def update_results(self):
        try:
            conexion = DatabaseManager.conectar_bd()
            if conexion:
                cursor = conexion.cursor()
                query = """
                    SELECT titulo, contenido, url, fecha
                    FROM monitoreo_web
                    ORDER BY fecha DESC
                    LIMIT 5
                """
                cursor.execute(query)
                results = cursor.fetchall()
                
                self.results_table.setRowCount(0)
                for result in results:
                    row_position = self.results_table.rowCount()
                    self.results_table.insertRow(row_position)
                    for column, data in enumerate(result):
                        self.results_table.setItem(row_position, column, QTableWidgetItem(str(data)))

                cursor.close()
                conexion.close()
        except Exception as e:
            self.status_label.setText(f"Error updating results: {str(e)}")

    def closeEvent(self, event):
        if self.scraper_thread and self.scraper_thread.running:
            self.scraper_thread.terminate()
            self.scraper_thread.wait()
        event.accept()