from PySide6.QtWidgets import QWidget, QVBoxLayout
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import psutil
import time
import numpy as np
from collections import deque
import matplotlib.pyplot as plt
import threading

class StatsCollector(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_data()
        self.setup_plots()
        self.setup_layout()
        self.running = False
        self.lock = threading.Lock()

    def setup_data(self):
        self.net_io_counters = psutil.net_io_counters()
        self.prev_bytes_sent = self.net_io_counters.bytes_sent
        self.prev_bytes_recv = self.net_io_counters.bytes_recv

        self.max_points = 60
        self.times = deque(maxlen=self.max_points)
        self.cpu_data = deque(maxlen=self.max_points)
        self.memory_data = deque(maxlen=self.max_points)
        self.disk_data = deque(maxlen=self.max_points)
        self.network_sent_data = deque(maxlen=self.max_points)
        self.network_recv_data = deque(maxlen=self.max_points)

    def setup_plots(self):
        self.fig = Figure(figsize=(12, 8))
        self.fig.patch.set_facecolor('#2b2b2b')

        # CPU Plot
        self.ax_cpu = self.fig.add_subplot(221)
        self.cpu_line, = self.ax_cpu.plot([], [], 'c-', label='CPU %')
        self.configure_subplot(self.ax_cpu, 'CPU Usage')

        # Memory Plot
        self.ax_mem = self.fig.add_subplot(222)
        self.mem_line, = self.ax_mem.plot([], [], 'g-', label='Memory %')
        self.configure_subplot(self.ax_mem, 'Memory Usage')

        # Disk Plot
        self.ax_disk = self.fig.add_subplot(223)
        self.disk_line, = self.ax_disk.plot([], [], 'm-', label='Disk %')
        self.configure_subplot(self.ax_disk, 'Disk Usage')

        # Network Plot
        self.ax_net = self.fig.add_subplot(224)
        self.net_sent_line, = self.ax_net.plot([], [], 'r-', label='Upload')
        self.net_recv_line, = self.ax_net.plot([], [], 'b-', label='Download')
        self.configure_subplot(self.ax_net, 'Network Speed (KB/s)')
        self.ax_net.legend()

        self.fig.tight_layout()

    def configure_subplot(self, ax, title):
        ax.set_title(title, color='white')
        ax.set_facecolor('#1c1c1c')
        ax.tick_params(colors='white')
        ax.grid(True)
        for spine in ax.spines.values():
            spine.set_color('white')

    def setup_layout(self):
        layout = QVBoxLayout(self)
        self.canvas = FigureCanvasQTAgg(self.fig)
        layout.addWidget(self.canvas)

    def update_plots(self):
        x = np.arange(len(self.times))
        
        self.cpu_line.set_data(x, self.cpu_data)
        self.mem_line.set_data(x, self.memory_data)
        self.disk_line.set_data(x, self.disk_data)
        self.net_sent_line.set_data(x, self.network_sent_data)
        self.net_recv_line.set_data(x, self.network_recv_data)

        for ax in [self.ax_cpu, self.ax_mem, self.ax_disk]:
            ax.set_xlim(0, len(self.times))
            ax.set_ylim(0, 100)

        self.ax_net.set_xlim(0, len(self.times))
        if self.network_sent_data and self.network_recv_data:
            max_net = max(max(self.network_sent_data), max(self.network_recv_data))
            self.ax_net.set_ylim(0, max_net * 1.1)

        self.canvas.draw()

    def collect_stats(self):
        self.collect_cpu()
        self.collect_memory()
        self.collect_disk()
        self.collect_network()
        self.update_plots()

    def collect_cpu(self):
        self.cpu_data.append(psutil.cpu_percent())
        self.times.append(time.strftime('%H:%M:%S'))

    def collect_memory(self):
        self.memory_data.append(psutil.virtual_memory().percent)

    def collect_disk(self):
        self.disk_data.append(psutil.disk_usage('/').percent)

    def collect_network(self):
        net_io = psutil.net_io_counters()
        sent_speed = (net_io.bytes_sent - self.prev_bytes_sent) / 1024
        recv_speed = (net_io.bytes_recv - self.prev_bytes_recv) / 1024
        
        self.network_sent_data.append(sent_speed)
        self.network_recv_data.append(recv_speed)
        
        self.prev_bytes_sent = net_io.bytes_sent
        self.prev_bytes_recv = net_io.bytes_recv

    def start_collecting(self, continuous=False):
        self.running = True
        while self.running:
            with self.lock:
                self.collect_stats()
            if not continuous:
                break

    def stop(self):
        with self.lock:
            self.running = False

    def get_stats(self):
        with self.lock:
            return {}

    def closeEvent(self, event):
        try:
            self.stop()
            plt.close(self.fig)
        except Exception as e:
            print(f"Error stopping stats collector: {e}")
        event.accept()