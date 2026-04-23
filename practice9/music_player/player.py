import pygame
import os
import glob


class MusicPlayer:
    def __init__(self):
        pygame.mixer.init()

        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.music_folder = os.path.join(base_dir, "music", "sample_tracks")

        self.playlist = []
        self.current_index = 0
        self.is_playing = False
        self.manual_change = False

        self._load_playlist()

    def _load_playlist(self):
        for ext in ("*.mp3", "*.wav", "*.ogg"):
            self.playlist += glob.glob(os.path.join(self.music_folder, ext))
        self.playlist.sort()

    def current_track_name(self):
        if not self.playlist:
            return "No tracks found"
        return os.path.basename(self.playlist[self.current_index])

    def play(self):
        if not self.playlist:
            return

        pygame.mixer.music.stop()
        pygame.mixer.music.unload()

        pygame.mixer.music.load(self.playlist[self.current_index])
        pygame.mixer.music.play()
        self.is_playing = True

    def stop(self):
        pygame.mixer.music.stop()
        pygame.mixer.music.unload()
        self.is_playing = False
        self.manual_change = True  

    def next_track(self):
        if not self.playlist:
            return

        self.manual_change = True
        self.current_index = (self.current_index + 1) % len(self.playlist)
        self.play()

    def previous_track(self):
        if not self.playlist:
            return

        self.manual_change = True
        self.current_index = (self.current_index - 1) % len(self.playlist)
        self.play()