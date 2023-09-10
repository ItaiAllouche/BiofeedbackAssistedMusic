from vlc import Instance
import vlc
from typing import List
import time
import os
import librosa

class Player:
    def __init__(self, songs: List[str], speed_change: float = 5):
        '''
        songs: list of paths to songs playlist
        speed_change: amount of change to playback speed in percentage
        '''
        self._player = Instance('--loop')
        self._songs = songs
        self._speed_change = speed_change
        self._tempo = []
        self._current_song = 0        
        self._media_list = self._player.media_list_new()
        for i, song in enumerate(songs):
            self._media_list.add_media(self._player.media_new(song))
            current_file  = librosa.load(song)
            y, sr = current_file
            tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
            self._tempo.insert(len(self._tempo), tempo)

        self._list_player = self._player.media_list_player_new()
        self._list_player.set_media_list(self._media_list)
        self._list_player.set_media_player(self._player.media_player_new())
        self._media_player = self._list_player.get_media_player()
        self._level = 0

    def play(self):
        self._list_player.play()
    def next(self):
        self._list_player.next()
        self._current_song += 1
    def pause(self):
        self._list_player.pause()
    def previous(self):
        self._list_player.previous()
        self._current_song -= 1
    def stop(self):
        self._list_player.stop()
    def up(self, speed_change: float = None):
        self._media_player.set_rate(1 + (self._speed_change if(speed_change is None) else speed_change)/100)
        self._level += 1
        self._tempo[self._current_song] += (self._tempo[self._current_song]*self._speed_change/100)
    def down(self, speed_change: float = None):
        self._media_player.set_rate(1 - (self._speed_change if(speed_change is None) else speed_change)/100)
        self._level -= 1
        self._tempo[self._current_song] -= (self._tempo[self._current_song]*self._speed_change/100)
    def get_level(self) -> int:
        return self._level
    def get_tempo(self) -> float:
        return self._tempo[self._current_song]