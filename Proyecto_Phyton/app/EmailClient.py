import smtplib
import imaplib
import email
import threading
import subprocess
import re
import sqlite3
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from PySide6.QtWidgets import QTextEdit
from PySide6.QtCore import QObject, Signal

class EmailClient(QObject):
    emails_received = Signal(list)  # Signal to emit received emails

    def __init__(self, email_user, password):
        super().__init__()
        self.email_user = email_user
        self.password = password
        self.server_ip = self.detect_network()  # Detecta la red y asigna la IP
        print(f"Using server IP: {self.server_ip}")  # Debug print

        self.ports = {
            "EMAIL": 20000,
            "SMTP": 25,
            "SMTP-S": 465,
            "SMTP-SUBMISSION": 587,
            "IMAP": 143,
            "IMAP-S": 993
        }
        self.unread_count = 0

        # Initialize database
        self.init_db()

    def init_db(self):
        self.conn = sqlite3.connect('emails.db', check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS emails (
                id INTEGER PRIMARY KEY,
                sender TEXT,
                subject TEXT,
                body TEXT,
                is_read INTEGER DEFAULT 0
            )
        ''')
        self.conn.commit()

    def detect_network(self):
        """Detecta la red WiFi en Windows y cambia la IP del servidor de correo."""
        try:
            result = subprocess.run(["netsh", "wlan", "show", "interfaces"], capture_output=True, text=True)
            match = re.search(r"SSID\s*:\s*(.+)", result.stdout)
            if match:
                ssid = match.group(1).strip()
                print(f"Conectado a: {ssid}")

                # Definir las IP según la red WiFi detectada
                network_ips = {
                    "2DAM": "192.168.120.103",
                    "Caseta": "s1.ieslamar.org" 
                }
                if ssid == "2DAM":
                    self.email_user = "borja@psp.ieslamar.org"
                    self.password = "1234"
                else:
                    self.email_user = "borja@fp.ieslamar.org"
                    self.password = "1234"
                    network_ips.get(ssid, "s1.ieslamar.org")  # IP por defecto si la red no está en la lista

                return network_ips.get(ssid, "s1.ieslamar.org")  # IP por defecto si la red no está en la lista
        except Exception as e:
            print(f"Error detectando la red: {e}")

        return "s1.ieslamar.org"  # IP predeterminada si no se puede detectar la red

    def enviar_correo(self, destinatario, asunto, mensaje):
        """Envío de correo usando la IP detectada."""
        def enviar():
            try:
                print(f"Connecting to server at {self.server_ip}:{self.ports['SMTP']}")  # Debug print
                with smtplib.SMTP(self.server_ip, self.ports["SMTP"]) as smtp:
                    smtp.login(self.email_user, self.password)
                    msg = MIMEMultipart()
                    msg["From"] = self.email_user
                    msg["To"] = destinatario
                    msg["Subject"] = asunto
                    msg.attach(MIMEText(mensaje, "plain"))
                    smtp.sendmail(self.email_user, destinatario, msg.as_string())
                    print("Correo enviado correctamente.")
            except Exception as e:
                print(f"Error al enviar el correo: {e}")

        thread = threading.Thread(target=enviar)
        thread.start()

    def recibir_correos(self):
        """Recibe correos usando la IP detectada."""
        def recibir():
            conn = sqlite3.connect('emails.db', check_same_thread=False)
            cursor = conn.cursor()
            try:
                print(f"Connecting to IMAP server at {self.server_ip}:{self.ports['IMAP-S']}")  # Debug print
                with imaplib.IMAP4_SSL(self.server_ip, self.ports["IMAP-S"]) as mail:
                    mail.login(self.email_user, self.password)
                    mail.select("inbox")
                    status, mensajes_no_leidos = mail.search(None, 'ALL')
                    todos_los_mensajes = mensajes_no_leidos[0].split()
                    self.unread_count = len([msg for msg in todos_los_mensajes if b'\\Seen' not in mail.fetch(msg, '(FLAGS)')[1][0]])

                    emails = []
                    
                    for num in todos_los_mensajes:
                        status, data = mail.fetch(num, '(RFC822)')
                        mensaje = email.message_from_bytes(data[0][1])
                        de = mensaje["From"]
                        asunto = mensaje["Subject"]
                        cuerpo = ""
                        if mensaje.is_multipart():
                            for part in mensaje.walk():
                                if part.get_content_type() == "text/plain":
                                    cuerpo = part.get_payload(decode=True).decode()
                                    break
                        else:
                            cuerpo = mensaje.get_payload(decode=True).decode()
                        
                        # Save email to database
                        cursor.execute('''
                            INSERT INTO emails (sender, subject, body)
                            VALUES (?, ?, ?)
                        ''', (de, asunto, cuerpo))
                        conn.commit()

                        emails.append((de, asunto, cuerpo))
                        mail.store(num, '+FLAGS', '\\Seen')

                    self.emails_received.emit(emails)  # Emit the signal with the email details
            except Exception as e:
                self.emails_received.emit([(f"Error al recibir correos: {e}", "", "")])
            finally:
                cursor.close()
                conn.close()

        thread = threading.Thread(target=recibir)
        thread.start()

    def get_unread_count(self):
        self.cursor.execute('SELECT COUNT(*) FROM emails WHERE is_read = 0')
        return self.cursor.fetchone()[0]

    def mark_as_read(self, email_id):
        self.cursor.execute('UPDATE emails SET is_read = 1 WHERE id = ?', (email_id,))
        self.conn.commit()

    def cleanup(self):
        """Limpieza al finalizar."""
        self.conn.close()
