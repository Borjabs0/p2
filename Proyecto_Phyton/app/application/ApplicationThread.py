import threading
import subprocess
import os
from typing import Dict, Optional
from PySide6.QtCore import QThread, Signal

class ApplicationRunner(QThread):
    app_started = Signal(str)  # Signal when app starts
    app_error = Signal(str)    # Signal when error occurs
    
    def __init__(self, app_name: str, app_path: str, args: Optional[list] = None):
        super().__init__()
        self.app_name = app_name
        self.app_path = app_path
        self.args = args or []
        self.process = None

    def run(self):
        try:
            cmd = [self.app_path] + self.args
            self.process = subprocess.Popen(cmd)
            self.app_started.emit(f"{self.app_name} started successfully")
            self.process.wait()
        except Exception as e:
            self.app_error.emit(f"Error starting {self.app_name}: {str(e)}")

class ApplicationThread:
    def __init__(self):
        self.running_apps: Dict[str, subprocess.Popen] = {}
        self.app_threads: Dict[str, ApplicationRunner] = {}

        self.app_paths = {
            'vscode': r'C:\Users\borja\AppData\Local\Programs\Microsoft VS Code\Code.exe',
            'edge': r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
            'explorer': r'explorer.exe',
            'notepad': r'notepad.exe'
        }

    def launch_application(self, app_name: str, args: Optional[list] = None):
        """
        Launches an application in a separate thread
        """
        if app_name not in self.app_paths:
            raise ValueError(f"Unknown application: {app_name}")

        app_path = self.app_paths[app_name]
        
        # Create and start new thread
        thread = ApplicationRunner(app_name, app_path, args)
        thread.app_started.connect(self._on_app_started)
        thread.app_error.connect(self._on_app_error)
        
        self.app_threads[app_name] = thread
        thread.start()

    def _on_app_started(self, message: str):
        print(message)

    def _on_app_error(self, error: str):
        print(error)

    def terminate_application(self, app_name: str):
        """
        Terminates a running application
        """
        if app_name in self.app_threads:
            thread = self.app_threads[app_name]
            if thread.process:
                thread.process.terminate()
            thread.quit()
            thread.wait()
            del self.app_threads[app_name]

    def terminate_all(self):
        """
        Terminates all running applications
        """
        for app_name in list(self.app_threads.keys()):
            self.terminate_application(app_name)