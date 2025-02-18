from PySide6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QGraphicsScene, 
                              QGraphicsView, QGraphicsEllipseItem, QLabel, QHBoxLayout,
                              QComboBox, QSpinBox, QGroupBox)
from PySide6.QtCore import Qt, QTimer, QRectF, Signal, Slot, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QPen, QBrush, QColor, QPainter, QFont, QLinearGradient
import random

class RaceTrack(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(800, 600)  # Establece un tamaño fijo más ancho y más alto
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.setBackgroundBrush(self.create_gradient())
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setRenderHint(QPainter.Antialiasing)
        
    def create_gradient(self):
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QColor(40, 40, 40))
        gradient.setColorAt(1, QColor(20, 20, 20))
        return QBrush(gradient)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.scene.setSceneRect(0, 0, self.width(), self.height())
        self.update_track()

    def update_track(self):
        self.scene.clear()
        width = self.width()
        height = self.height()
        
        # Draw finish line with checkered pattern
        square_size = 10
        for i in range(0, int(height/square_size)):
            color = Qt.white if i % 2 == 0 else Qt.black
            self.scene.addRect(width-20, i*square_size, square_size, square_size, 
                             QPen(Qt.transparent), QBrush(color))
        
        # Draw lanes with dashed lines
        for i in range(4):
            y = (i + 1) * height / 5
            dash_pen = QPen(QColor(200, 200, 200), 1, Qt.DashLine)
            self.scene.addLine(0, y, width, y, dash_pen)

class Ball(QGraphicsEllipseItem):
    def __init__(self, color, name, parent=None):
        super().__init__(0, 0, 25, 25, parent)
        self.name = name
        self.setPos(0, 0)
        gradient = QLinearGradient(0, 0, 25, 25)
        base_color = QColor(color)
        gradient.setColorAt(0.2, base_color.lighter(150))
        gradient.setColorAt(0.8, base_color)
        self.setBrush(QBrush(gradient))
        self.setPen(QPen(Qt.white, 2))
        self.x_pos = 0
        self.finished = False
        self.speed = random.uniform(0.5, 1.5)  # Asignar una velocidad aleatoria a cada bola
        self.boost = 1.0
        self.label = None
        self.active = True

    def add_label(self):
        if self.scene() and not self.label:
            self.label = self.scene().addText(self.name, QFont("Arial", 8))
            self.label.setDefaultTextColor(Qt.white)
            self.update_label_position()

    def update_label_position(self):
        if self.label:
            self.label.setPos(self.x_pos, self.y() - 20)

        
    def move_forward(self, speed):
        if not self.active or self.finished:
            return False
        try:
            self.x_pos += speed * self.boost
            self.setPos(self.x_pos, self.y())
            self.update_label_position()
            if self.x_pos >= (self.scene().width() - 30):
                self.finished = True
                return True
            return False
        except:
            self.active = False
            return False

class RaceGame(QWidget):
    game_finished = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.scores = {"Player 1": 0, "Player 2": 0, "Player 3": 0, "Player 4": 0}
        self.setup_ui()
        self.running = False
        self.winner = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_race)
        self.race_speed = 5
        self.create_balls()  # Ensure balls are created and positioned correctly at the start

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        # Score display
        self.score_label = QLabel("Scores: ")
        main_layout.addWidget(self.score_label)
        
        # Race track
        self.track = RaceTrack()
        main_layout.addWidget(self.track)
        
        self.track.update_track()  # Actualizar la pista

        
        # Controls group
        controls = QGroupBox("Race Controls")
        controls_layout = QHBoxLayout()
        
        # Speed control
        speed_layout = QVBoxLayout()
        speed_label = QLabel("Race Speed:")
        self.speed_spin = QSpinBox()
        self.speed_spin.setRange(1, 10)
        self.speed_spin.setValue(5)
        self.speed_spin.valueChanged.connect(self.update_race_speed)
        speed_layout.addWidget(speed_label)
        speed_layout.addWidget(self.speed_spin)
        controls_layout.addLayout(speed_layout)
        
        # Buttons
        button_layout = QVBoxLayout()
        self.start_button = QPushButton("Start Race")
        self.start_button.clicked.connect(self.start_race)
        self.reset_button = QPushButton("Reset Race")
        self.reset_button.clicked.connect(self.reset_race)
        self.reset_button.setEnabled(False)
        self.stop_button = QPushButton("Stop Race")  # Nuevo botón para detener la carrera
        self.stop_button.clicked.connect(self.stop_race)
        self.stop_button.setEnabled(False)
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.reset_button)
        button_layout.addWidget(self.stop_button)  # Añadir el botón de detener al layout
        controls_layout.addLayout(button_layout)
        
        controls.setLayout(controls_layout)
        main_layout.addWidget(controls)
        
        self.update_score_display()

    def create_balls(self):
        self.balls = []
        colors = ["red", "blue", "green", "yellow"]
        names = ["Player 1", "Player 2", "Player 3", "Player 4"]
        height = self.track.height()
        
        for i, (color, name) in enumerate(zip(colors, names)):
            ball = Ball(color, name)
            y_pos = (i + 1) * height / 5 - 10
            ball.setPos(0, y_pos)
            self.track.scene.addItem(ball)  # Add ball to scene first
            ball.add_label()  # Then create the label
            self.balls.append(ball)

    def update_score_display(self):
        score_text = "Scores: " + " | ".join(
            f"{name}: {score}" for name, score in self.scores.items()
        )
        self.score_label.setText(score_text)

    @Slot()
    def update_race_speed(self, value):
        self.race_speed = value

    @Slot()
    def start_race(self):
        self.running = True
        self.start_button.setEnabled(False)
        self.reset_button.setEnabled(False)
        self.stop_button.setEnabled(True)  # Habilitar el botón de detener cuando la carrera comienza
        self.speed_spin.setEnabled(False)
        self.timer.start(50)

    @Slot()
    def stop_race(self):
        self.running = False
        self.timer.stop()
        self.start_button.setEnabled(True)
        self.reset_button.setEnabled(True)
        self.stop_button.setEnabled(False)  # Deshabilitar el botón de detener cuando la carrera se detiene
        self.speed_spin.setEnabled(True)

    @Slot()
    def update_race(self):
        if not self.running:
            return

        active_balls = [ball for ball in self.balls if ball.active and not ball.finished]
        if not active_balls:
            self.end_race()
            return

        for ball in active_balls:
            try:
                if ball.move_forward(self.race_speed * ball.speed):  # Usar la velocidad específica de cada bola
                    self.winner = ball
                    self.end_race()
                    return
            except RuntimeError:
                ball.active = False

    def cleanup(self):
        self.timer.stop()
        self.running = False
        for ball in self.balls:
            if ball.scene():
                ball.scene().removeItem(ball)
        self.balls.clear()

    def closeEvent(self, event):
        self.cleanup()
        super().closeEvent(event)

    def end_race(self):
        self.running = False
        self.timer.stop()
        self.reset_button.setEnabled(True)
        self.speed_spin.setEnabled(True)
        
        # Update scores
        self.scores[self.winner.name] += 1
        self.update_score_display()
        
        winner_message = (f"{self.winner.name} wins!\n"
                         f"Final position: {self.get_race_positions()}")
        self.game_finished.emit(winner_message)

    def get_race_positions(self):
        positions = sorted(self.balls, key=lambda b: b.x_pos, reverse=True)
        return " > ".join(ball.name for ball in positions)

    @Slot()
    def reset_race(self):
        self.track.scene.clear()
        self.track.update_track()
        self.create_balls()
        self.winner = None
        self.start_button.setEnabled(True)
        self.reset_button.setEnabled(False)
        self.stop_button.setEnabled(False)  # Asegurarse de que el botón de detener esté deshabilitado

    def closeEvent(self, event):
        self.timer.stop()
        event.accept()