from PySide6.QtCore import QThread, Signal
import requests

class WeatherThread(QThread):
    update_temp = Signal(str)

    def __init__(self, update_temp_callback):
        super().__init__()
        self.update_temp.connect(update_temp_callback)
        self.running = True

    def run(self):
        while self.running:
            try:
                # Usando OpenWeatherMap API
                API_KEY = "850530a0bb411e634ebd69b94c322a14"
                url = f"http://api.openweathermap.org/data/2.5/weather?q=Teulada&appid={API_KEY}&units=metric"
                response = requests.get(url)

                if response.status_code != 200:
                    self.update_temp.emit("Error al obtener datos del clima")
                    return

                data = response.json()
                temp = data['main']['temp']
                city = data['name']
                self.update_temp.emit(f"Temperatura actual en {city}: {temp}°C")
            except Exception as e:
                self.update_temp.emit(f"Error: {str(e)}")
            self.sleep(60)  # Update every 60 seconds

    def stop(self):
        self.running = False
        self.wait()  # Ensure the thread stops completely