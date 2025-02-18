from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import QTimer, Slot
from .Stats_Collector import StatsCollector

class SystemMonitor(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.setup_timers()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Status labels
        self.cpu_label = QLabel("CPU: --")
        self.memory_label = QLabel("Memory: --")
        self.disk_label = QLabel("Disk: --")
        self.network_label = QLabel("Network: --")
        
        for label in [self.cpu_label, self.memory_label, 
                     self.disk_label, self.network_label]:
            layout.addWidget(label)

        # Stats collector with plots
        self.stats_collector = StatsCollector()
        layout.addWidget(self.stats_collector)

    def setup_timers(self):
        # Timer for collecting stats
        self.collection_timer = QTimer(self)
        self.collection_timer.timeout.connect(self.collect_stats)
        self.collection_timer.start(1000)  # 1 seconds

        # Timer for updating labels
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_labels)
        self.update_timer.start(1000)  # 1 second

    @Slot()
    def collect_stats(self):
        self.stats_collector.collect_stats()

    @Slot()
    def update_labels(self):
        if self.stats_collector.cpu_data:
            self.cpu_label.setText(f"CPU: {self.stats_collector.cpu_data[-1]}%")
            self.memory_label.setText(f"Memory: {self.stats_collector.memory_data[-1]}%")
            self.disk_label.setText(f"Disk: {self.stats_collector.disk_data[-1]}%")
            self.network_label.setText(
                f"Network: ↑{self.stats_collector.network_sent_data[-1]:.1f} KB/s | "
                f"↓{self.stats_collector.network_recv_data[-1]:.1f} KB/s"
            )

    def closeEvent(self, event):
        self.collection_timer.stop()
        self.update_timer.stop()
        event.accept()