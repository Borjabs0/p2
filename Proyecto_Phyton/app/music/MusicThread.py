import os
import pygame
from PySide6.QtCore import QThread, Signal

class MusicThread(QThread):
    status_changed = Signal(str)  # Signal for status updates
    playback_finished = Signal()  # Signal when song finishes

    def __init__(self):
        super().__init__()
        self.playing = False
        self.current_song = None
        pygame.mixer.init()

    def run(self):
        while True:
            if self.playing and self.current_song:
                if not pygame.mixer.music.get_busy():
                    self.status_changed.emit("Playback finished")
                    self.playback_finished.emit()
                    self.playing = False
            self.msleep(100)  # Check every 100ms

    def play_song(self, song_path):
        if not song_path:
            self.status_changed.emit("Error: No song selected.")
            return

        try:
            self.current_song = song_path
            print(f"Playing song: {song_path}")  # Debug message
            pygame.mixer.music.load(song_path)
            pygame.mixer.music.play()
            self.playing = True
            self.status_changed.emit(f"Playing: {os.path.basename(song_path)}")
        except Exception as e:
            self.status_changed.emit(f"Error playing song: {str(e)}")

    def pause_song(self):
        if self.playing:
            pygame.mixer.music.pause()
            self.playing = False
            self.status_changed.emit("Paused")
        else:
            pygame.mixer.music.unpause()
            self.playing = True
            self.status_changed.emit("Playing")

    def stop_song(self):
        pygame.mixer.music.stop()
        self.playing = False
        self.current_song = None  # Clear the current song
        self.status_changed.emit("Stopped")

    def is_playing(self):
        return self.playing

    def cleanup(self):
        try:
            self.stop_song()
            pygame.mixer.quit()
        except Exception as e:
            print(f"Error cleaning up music thread: {e}")