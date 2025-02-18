from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                              QPushButton, QLabel, QTabWidget, QFrame,
                              QListWidget, QLineEdit, QTextEdit, QFileDialog,
                              QTableWidget, QTableWidgetItem, QHeaderView)
from PySide6.QtCore import Qt, QTimer, Slot
from application.ApplicationThread import ApplicationThread
from system_monitor.Stats_Collector import StatsCollector
from utils.Enlaces import Enlaces
from music.MusicThread import MusicThread
from game.RaceGame import RaceGame
from weather.WeatherThread import WeatherThread
from system_monitor.System_Monitor import SystemMonitor
from Scrapper.Scrapper import ScraperApp
from ui.BrowserWidget import BrowserWidget
from email_client.EmailClient import EmailClient
from chat.Chat import ChatWidget
import pygame
import datetime
import os
import threading
from asyncio import Queue
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Main Window")
        self.resize(1200, 800)

        # Initialize pygame for audio
        pygame.init()
        pygame.mixer.init()

        # Create central widget and main layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)

        # Create panels
        self.create_left_panel()
        self.create_center_panel()
        self.create_right_panel()
        self.create_bottom_bar()

        # Start periodic updates
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)
        self.start_weather_thread()

        # Initialize EmailClient
        self.email_client = EmailClient("", "")
        self.email_client.emails_received.connect(self.display_emails)  

    def create_left_panel(self):
        left_panel = QFrame()
        left_layout = QVBoxLayout(left_panel)

        self.app_thread_manager = ApplicationThread()
        self.enlaces = Enlaces()

        # Applications section
        apps_frame = QFrame()
        apps_frame.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        apps_layout = QVBoxLayout(apps_frame)
        apps_layout.addWidget(QLabel("Applications"))

        app_buttons = {
            "Visual Code": self.launch_vscode,
            "Edge": self.launch_edge,
            "File Explorer": self.launch_explorer,
            "Notepad": self.launch_notepad
        }

        for name, action in app_buttons.items():
            btn = QPushButton(name)
            btn.setStyleSheet("QPushButton { padding: 5px; }")
            btn.clicked.connect(action)
            apps_layout.addWidget(btn)

        left_layout.addWidget(apps_frame)

        # Links section
        links_frame = QFrame()
        links_frame.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        links_layout = QVBoxLayout(links_frame)
        links_layout.addWidget(QLabel("Quick Links"))

        url_buttons = {
            "Google": self.open_google,
            "Github": self.open_github,
            "StackOverflow": self.open_stackoverflow
        }

        for name, action in url_buttons.items():
            btn = QPushButton(name)
            btn.setStyleSheet("QPushButton { padding: 5px; }")
            btn.clicked.connect(action)
            links_layout.addWidget(btn)

        left_layout.addWidget(links_frame)
        left_layout.addStretch()

        self.main_layout.addWidget(left_panel)

    def create_center_panel(self):
        center_panel = QTabWidget()
        
        # Browser tab
        self.tab_nav = QWidget()
        center_panel.addTab(self.tab_nav, "Browser")
        nav_content = BrowserWidget(self.tab_nav)

        # Scraping tab
        self.tab_scraping = QWidget()
        center_panel.addTab(self.tab_scraping, "Web Scraping")
        self.scrapper = ScraperApp(self.tab_scraping)

        # Resource monitor tab
        self.tab_resources = QWidget()
        center_panel.addTab(self.tab_resources, "Resource Monitor")
        resource_layout = SystemMonitor(self.tab_resources)

        # Race game tab
        self.race_game_tab = QWidget()
        center_panel.addTab(self.race_game_tab, "Race Game")
        self.race_game = RaceGame(self.race_game_tab)

        # Chat tab
        self.tab_chat = QWidget()
        center_panel.addTab(self.tab_chat, "Chat")
        chat_layout = QVBoxLayout(self.tab_chat)
        self.chat_widget = ChatWidget(self.tab_chat)
        chat_layout.addWidget(self.chat_widget)

        # Email tab
        self.tab_email = QWidget()
        center_panel.addTab(self.tab_email, "Email")
        email_layout = QVBoxLayout(self.tab_email)

        # Email interface
        email_form = QFrame()
        email_form.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        form_layout = QVBoxLayout(email_form)

        self.email_table = QTableWidget()
        self.email_table.setColumnCount(3)
        self.email_table.setHorizontalHeaderLabels(["Sender", "Subject", "Message"])
        self.email_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.email_table.itemClicked.connect(self.show_email_details)
        form_layout.addWidget(self.email_table)

        self.email_display = QTextEdit()
        self.email_display.setReadOnly(True)
        form_layout.addWidget(self.email_display)

        # Email composition
        self.email_recipient_input = QLineEdit()
        self.email_recipient_input.setPlaceholderText("Recipient")
        form_layout.addWidget(self.email_recipient_input)

        self.email_subject_input = QLineEdit()
        self.email_subject_input.setPlaceholderText("Subject")
        form_layout.addWidget(self.email_subject_input)

        self.email_message_input = QTextEdit()
        self.email_message_input.setPlaceholderText("Message")
        form_layout.addWidget(self.email_message_input)

        # Email buttons
        button_layout = QHBoxLayout()
        send_email_button = QPushButton("Send Email")
        send_email_button.clicked.connect(self.send_email)
        receive_email_button = QPushButton("Receive Emails")
        receive_email_button.clicked.connect(self.receive_emails)
        button_layout.addWidget(send_email_button)
        button_layout.addWidget(receive_email_button)
        form_layout.addLayout(button_layout)

        email_layout.addWidget(email_form)

        self.main_layout.addWidget(center_panel)

    def create_right_panel(self):
        right_panel = QFrame()
        right_panel.setFixedWidth(250)
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(5, 5, 5, 5)

        # Music section
        self.music_status_label = QLabel("Music Player")
        right_layout.addWidget(self.music_status_label)

        music_controls = QHBoxLayout()
        music_controls.setSpacing(2)
        for action in [("Play", self.play_music), ("Pause", self.pause_music), ("Stop", self.stop_music)]:
            btn = QPushButton(action[0])
            btn.setMaximumHeight(25)
            btn.clicked.connect(action[1])
            music_controls.addWidget(btn)
        right_layout.addLayout(music_controls)

        # File chooser
        self.file_chooser_button = QPushButton("Choose Music Folder")
        self.file_chooser_button.clicked.connect(self.choose_music_folder)
        right_layout.addWidget(self.file_chooser_button)

        self.file_chooser = QListWidget()
        self.file_chooser.setMaximumHeight(150)
        self.file_chooser.itemClicked.connect(self.select_song)
        right_layout.addWidget(self.file_chooser)
        self.load_music_files()

        self.music_thread = MusicThread()
        self.music_thread.status_changed.connect(self.update_music_status)
        self.music_thread.start()

        # Add stretch to push everything to the top
        right_layout.addStretch()

        self.main_layout.addWidget(right_panel)

    def choose_music_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Music Folder", os.path.expanduser("~"))
        if folder:
            self.load_music_files(folder)

    def load_music_files(self, music_dir=None):
        self.file_chooser.clear()
        for file in os.listdir(music_dir):
            if file.endswith(".mp3"):
                print(f"Found MP3 file: {file}")  # Debug message
                self.file_chooser.addItem(os.path.join(music_dir, file))

    def create_bottom_bar(self):
        bottom_bar = QFrame(self.centralWidget())
        bottom_layout = QHBoxLayout(bottom_bar)
        self.unread_emails_label = QLabel("Unread Emails: 0")
        self.temperature_label = QLabel("Local Temperature")
        self.time_label = QLabel("Date and Time")

        bottom_layout.addWidget(self.unread_emails_label)
        bottom_layout.addWidget(self.temperature_label)
        bottom_layout.addWidget(self.time_label, alignment=Qt.AlignRight)

        bottom_bar.setLayout(bottom_layout)
        self.statusBar().addWidget(bottom_bar)

    @Slot()
    def update_time(self):
        now = datetime.datetime.now()
        self.time_label.setText(now.strftime("%A, %d/%m/%Y - %H:%M:%S"))

    @Slot(str)
    def update_temp_label(self, temp):
        self.temperature_label.setText(temp)

    @Slot(str)
    def update_music_status(self, status):
        self.music_status_label.setText(status)

    @Slot()
    def select_song(self, item):
        self.current_song = item.text()
        self.music_status_label.setText(f"Selected: {os.path.basename(self.current_song)}")

    @Slot()
    def play_music(self):
        if hasattr(self, 'current_song'):
            self.music_thread.play_song(self.current_song)

    @Slot()
    def pause_music(self):
        self.music_thread.pause_song()

    @Slot()
    def stop_music(self):
        self.music_thread.stop_song()

    # Application launch methods
    @Slot()
    def launch_vscode(self):
        self.app_thread_manager.launch_application('vscode')

    @Slot()
    def launch_edge(self):
        self.app_thread_manager.launch_application('edge')

    @Slot()
    def launch_explorer(self):
        self.app_thread_manager.launch_application('explorer')

    @Slot()
    def launch_notepad(self):
        self.app_thread_manager.launch_application('notepad')

    # URL methods
    @Slot()
    def open_google(self):
        self.enlaces.abrir_google()

    @Slot()
    def open_github(self):
        self.enlaces.abrir_github()

    @Slot()
    def open_stackoverflow(self):
        self.enlaces.abrir_stackoverflow()

    # Resource monitoring methods
    @Slot()
    def show_resource_monitor(self):
        if not hasattr(self, 'stats_collector'):
            self.stats_collector = StatsCollector()
            self.stats_collector_thread = threading.Thread(
                target=self.stats_collector.start_collecting,
                args=(True,)
            )
            self.stats_collector_thread.daemon = True
            self.stats_collector_thread.start()

            self.resource_timer = QTimer(self)
            self.resource_timer.timeout.connect(self.update_resource_status)
            self.resource_timer.start(5000)
        else:
            self.stats_collector.stop()
            self.stats_collector_thread.join(timeout=1)
            self.resource_timer.stop()
            del self.stats_collector
            del self.stats_collector_thread

    @Slot()
    def update_resource_status(self):
        if hasattr(self, 'stats_collector'):
            stats = self.stats_collector.get_stats()
            # Update resource monitor UI with stats

    # Weather thread methods
    def start_weather_thread(self):
        self.weather_thread = WeatherThread(self.update_temp_label)
        self.weather_thread.start()

    @Slot()
    def send_email(self):
        recipient = self.email_recipient_input.text()
        subject = self.email_subject_input.text()
        message = self.email_message_input.toPlainText()
        self.email_client.enviar_correo(recipient, subject, message)

    @Slot()
    def receive_emails(self):
        self.email_client.recibir_correos()

    @Slot(list)
    def display_emails(self, emails):
        self.email_table.setRowCount(0)
        for email in emails:
            row_position = self.email_table.rowCount()
            self.email_table.insertRow(row_position)
            self.email_table.setItem(row_position, 0, QTableWidgetItem(email[0]))
            self.email_table.setItem(row_position, 1, QTableWidgetItem(email[1]))
            self.email_table.setItem(row_position, 2, QTableWidgetItem(email[2]))
        self.update_unread_emails_label()

    @Slot()
    def show_email_details(self, item):
        row = item.row()
        sender = self.email_table.item(row, 0).text()
        subject = self.email_table.item(row, 1).text()
        body = self.email_table.item(row, 2).text()
        self.email_display.setText(f"From: {sender}\nSubject: {subject}\n\n{body}")
        self.email_client.mark_as_read(row + 1)  # Assuming row + 1 is the email ID
        self.update_unread_emails_label()

    @Slot()
    def update_unread_emails_label(self):
        unread_count = self.email_client.get_unread_count()
        self.unread_emails_label.setText(f"Unread Emails: {unread_count}")

    def closeEvent(self, event):
        # Stop all threads
        try:
            if hasattr(self, 'music_thread'):
                self.music_thread.cleanup()
                self.music_thread.quit()
                self.music_thread.wait()
        except Exception as e:
            print(f"Error stopping music thread: {e}")

        try:
            if hasattr(self, 'stats_collector'):
                self.stats_collector.stop()
                self.stats_collector_thread.join(timeout=1)
        except Exception as e:
            print(f"Error stopping stats collector: {e}")

        try:
            if hasattr(self, 'weather_thread'):
                self.weather_thread.stop()
                self.weather_thread.wait()
        except Exception as e:
            print(f"Error stopping weather thread: {e}")

        try:
            if hasattr(self, 'chat_widget'):
                self.chat_widget.close()
        except Exception as e:
            print(f"Error closing chat widget: {e}")

        try:
            if hasattr(self, 'email_client'):
                self.email_client.cleanup()
        except Exception as e:
            print(f"Error closing email client: {e}")

        try:
            if hasattr(self, 'app_thread_manager'):
                self.app_thread_manager.terminate_all()
        except Exception as e:
            print(f"Error terminating application threads: {e}")

        event.accept()

if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())