import socket
import threading
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QTextEdit,
                              QPushButton, QLineEdit, QScrollArea,
                              QHBoxLayout, QLabel, QComboBox,
                              QFrame, QSplitter)
from PySide6.QtCore import Signal, Slot, QThread, Qt
from PySide6.QtGui import QFont, QColor, QTextCharFormat, QBrush, QTextCursor

class ServerThread(QThread):
    message_received = Signal(str, str)  # message, type (system, user, error)
    client_connected = Signal(str)
    client_disconnected = Signal(str)
    error_occurred = Signal(str)

    def __init__(self, host='0.0.0.0', port=3333):
        super().__init__()
        self.host = host
        self.port = port
        self.running = False
        self.server = None
        self.clients = []
        self.client_threads = []
        self.client_names = {}

    def run(self):
        try:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server.bind((self.host, self.port))
            self.server.listen(5)
            self.running = True
            self.message_received.emit(f"Server started on {self.host}:{self.port}", "system")

            while self.running:
                try:
                    self.server.settimeout(1.0)  # 1 second timeout
                    client, address = self.server.accept()
                    self.clients.append(client)
                    self.client_connected.emit(f"Client connected from {address}")

                    client_thread = threading.Thread(
                        target=self.handle_client,
                        args=(client, address)
                    )
                    client_thread.daemon = True
                    client_thread.start()
                    self.client_threads.append(client_thread)
                except socket.timeout:
                    continue
                except Exception as e:
                    if self.running:  # Only emit error if we're still supposed to be running
                        self.error_occurred.emit(f"Accept error: {str(e)}")
                    break

        except Exception as e:
            self.error_occurred.emit(f"Server error: {str(e)}")
        finally:
            self.cleanup()

    def handle_client(self, client, address):
        try:
            # First message should be the client's name
            name = client.recv(1024).decode('utf-8')
            self.client_names[client] = name
            self.message_received.emit(f"{name} has joined the chat", "system")

            while self.running:
                try:
                    client.settimeout(1.0)
                    message = client.recv(1024).decode('utf-8')
                    if message:
                        broadcast_message = f"{self.client_names[client]}: {message}"
                        self.message_received.emit(broadcast_message, "user")
                        self.broadcast(broadcast_message, client)
                except socket.timeout:
                    continue
                except:
                    break
        except:
            pass
        finally:
            if client in self.clients:
                name = self.client_names.get(client, f"Client {address}")
                self.clients.remove(client)
                if client in self.client_names:
                    del self.client_names[client]
                client.close()
                self.client_disconnected.emit(f"{name} has left the chat")

    def broadcast(self, message, sender=None):
        disconnected_clients = []
        for client in self.clients:
            if client != sender:
                try:
                    client.send(message.encode('utf-8'))
                except:
                    disconnected_clients.append(client)

        # Clean up disconnected clients
        for client in disconnected_clients:
            if client in self.clients:
                self.clients.remove(client)
                if client in self.client_names:
                    name = self.client_names[client]
                    del self.client_names[client]
                    self.client_disconnected.emit(f"{name} has disconnected")
                client.close()

    def cleanup(self):
        self.running = False
        if self.server:
            try:
                self.server.close()
            except:
                pass

        for client in self.clients:
            try:
                client.close()
            except:
                pass

        self.clients.clear()
        self.client_names.clear()

        for thread in self.client_threads:
            thread.join(timeout=1)
        self.client_threads.clear()

    def stop(self):
        self.running = False
        self.cleanup()

class ChatWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.username = "Borja"
        self.client_socket = None
        self.server_thread = None

    def setup_ui(self):
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # Server configuration
        server_config_frame = QFrame()
        server_config_frame.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        server_config_layout = QHBoxLayout(server_config_frame)

        self.server_host_input = QLineEdit("0.0.0.0")
        self.server_host_input.setMaximumWidth(150)
        self.server_port_input = QLineEdit("3333")
        self.server_port_input.setMaximumWidth(100)

        server_config_layout.addWidget(QLabel("Server Host:"))
        server_config_layout.addWidget(self.server_host_input)
        server_config_layout.addWidget(QLabel("Server Port:"))
        server_config_layout.addWidget(self.server_port_input)

        self.start_server_button = QPushButton("Start Server")
        self.start_server_button.clicked.connect(self.toggle_server)
        server_config_layout.addWidget(self.start_server_button)

        main_layout.addWidget(server_config_frame)

        # Client configuration
        config_frame = QFrame()
        config_frame.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        config_layout = QHBoxLayout(config_frame)

        self.host_input = QLineEdit("192.168.120.106")
        self.host_input.setMaximumWidth(150)
        self.port_input = QLineEdit("3333")
        self.port_input.setMaximumWidth(100)
        self.username_input = QLineEdit("Borja")
        self.username_input.setMaximumWidth(150)

        config_layout.addWidget(QLabel("Host:"))
        config_layout.addWidget(self.host_input)
        config_layout.addWidget(QLabel("Port:"))
        config_layout.addWidget(self.port_input)
        config_layout.addWidget(QLabel("Username:"))
        config_layout.addWidget(self.username_input)

        self.connect_button = QPushButton("Connect")
        self.connect_button.clicked.connect(self.toggle_connection)
        config_layout.addWidget(self.connect_button)

        main_layout.addWidget(config_frame)

        # Chat display area with custom formatting
        self.chat_area = QTextEdit()
        self.chat_area.setReadOnly(True)
        self.chat_area.setMinimumHeight(300)

        # Set default font
        font = QFont("Arial", 10)
        self.chat_area.setFont(font)

        main_layout.addWidget(self.chat_area)

        # Message input area
        input_layout = QHBoxLayout()

        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("Type your message here...")
        self.message_input.returnPressed.disconnect()  # Disconnect any existing connections
        self.message_input.returnPressed.connect(self.send_message)

        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_message)
        self.send_button.setMaximumWidth(100)

        input_layout.addWidget(self.message_input)
        input_layout.addWidget(self.send_button)

        main_layout.addLayout(input_layout)

        # Status bar
        self.status_bar = QLabel("Not connected")
        self.status_bar.setStyleSheet("color: gray;")
        main_layout.addWidget(self.status_bar)

    @Slot()
    def toggle_server(self):
        if not self.server_thread:
            try:
                host = self.server_host_input.text()
                port = int(self.server_port_input.text())
                self.server_thread = ServerThread(host, port)
                self.server_thread.message_received.connect(self.handle_message)
                self.server_thread.client_connected.connect(self.handle_message)
                self.server_thread.client_disconnected.connect(self.handle_message)
                self.server_thread.error_occurred.connect(self.handle_error)
                self.server_thread.start()

                self.start_server_button.setText("Stop Server")
                self.status_bar.setText(f"Server running on {host}:{port}")
                self.status_bar.setStyleSheet("color: green;")
            except Exception as e:
                self.handle_error(f"Failed to start server: {str(e)}")
        else:
            self.stop_server()

    def stop_server(self):
        if self.server_thread:
            self.server_thread.stop()
            self.server_thread.wait()
            self.server_thread = None
            self.start_server_button.setText("Start Server")
            self.status_bar.setText("Server stopped")
            self.status_bar.setStyleSheet("color: gray;")

    @Slot()
    def toggle_connection(self):
        if not self.client_socket:
            try:
                self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.client_socket.connect((self.host_input.text(), int(self.port_input.text())))
                self.username = self.username_input.text()
                self.client_socket.send(self.username.encode('utf-8'))

                self.connect_button.setText("Disconnect")
                self.status_bar.setText("Connected")
                self.status_bar.setStyleSheet("color: green;")
                self.host_input.setEnabled(False)
                self.port_input.setEnabled(False)
                self.username_input.setEnabled(False)

                self.listen_thread = threading.Thread(target=self.listen_for_messages)
                self.listen_thread.daemon = True
                self.listen_thread.start()
            except Exception as e:
                self.handle_error(f"Failed to connect: {str(e)}")
        else:
            self.disconnect()

    def listen_for_messages(self):
        try:
            while True:
                message = self.client_socket.recv(1024).decode('utf-8')
                if message:
                    self.handle_message(message, "user")
                else:
                    break
        except ConnectionAbortedError as e:
            self.handle_error(f"Connection aborted: {str(e)}")
        except Exception as e:
            self.handle_error(f"Connection error: {str(e)}")
        finally:
            self.disconnect()

    @Slot()
    def send_message(self):
        message = self.message_input.text().strip()
        if message and self.client_socket:
            try:
                self.client_socket.send(message.encode('utf-8'))
                self.format_message(f"{self.username}: {message}", "user")  # Only format the message for the sender
                self.message_input.clear()
            except Exception as e:
                self.handle_error(f"Failed to send message: {str(e)}")

    def disconnect(self):
        if self.client_socket:
            try:
                self.client_socket.close()
            except:
                pass
            self.client_socket = None
            self.connect_button.setText("Connect")
            self.status_bar.setText("Not connected")
            self.status_bar.setStyleSheet("color: gray;")
            self.host_input.setEnabled(True)
            self.port_input.setEnabled(True)
            self.username_input.setEnabled(True)

    def format_message(self, message, message_type):
        cursor = self.chat_area.textCursor()
        format = QTextCharFormat()

        if message_type == "system":
            format.setForeground(QBrush(QColor("gray")))
            format.setFontItalic(True)
        elif message_type == "error":
            format.setForeground(QBrush(QColor("red")))
            format.setFontWeight(QFont.Bold)
        else:  # user message
            format.setForeground(QBrush(QColor("black")))

        cursor.movePosition(QTextCursor.End)
        cursor.insertBlock()
        cursor.insertText(message, format)
        self.chat_area.setTextCursor(cursor)
        self.chat_area.ensureCursorVisible()

    @Slot(str, str)
    def handle_message(self, message, message_type="user"):
        self.format_message(message, message_type)

    @Slot(str)
    def handle_error(self, error):
        self.format_message(f"ERROR: {error}", "error")

    def closeEvent(self, event):
        self.disconnect()
        self.stop_server()
        event.accept()