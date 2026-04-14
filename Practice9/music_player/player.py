import pygame
import os

class Music_player:
    def __init__(self, music_folder):
        self.music_folder = music_folder
        self.playlist = self.load_tracks()
        self.current = 0
        self.playing = False

    def load_tracks(self):
        tracks = []
        for f_name in os.listdir(self.music_folder):
            if f_name.endswith(".mp3") or f_name.endswith(".wav"):
                tracks.append(os.path.join(self.music_folder, f_name))
        tracks.sort()
        return tracks
    
    def play(self):
        if not self.playlist:
            return
        
        track = self.playlist[self.current]
        pygame.mixer.music.load(track)
        pygame.mixer.music.play()
        self.playing = True

    def stop(self):
         pygame.mixer.music.stop()
         self.playing = False

    def next(self):
        if not self.playlist:
            return
        self.current = (self.current + 1) % len(self.playlist)
        self.play()

    def previous(self):
        if not self.playlist:
            return
        self.current = (self.current - 1) % len(self.playlist)
        self.play()

    def get_name(self):
        if not self.playlist:
            return "Not tracks fond"
        return os.path.basename(self.playlist[self.current])