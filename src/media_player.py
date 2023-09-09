from vlc import Instance
from typing import List
import time
import os

class Player:
    def __init__(self, songs: List[str], speed_change: float = 5):
        '''
        songs: list of paths to songs playlist
        speed_change: amount of change to playback speed in percentage
        '''
        self._player = Instance('--loop')
        self._songs = songs
        self._speed_change = speed_change
        self._media_list = self._player.media_list_new()
        for song in songs:
            self._media_list.add_media(self._player.media_new(song))
        self._list_player = self._player.media_list_player_new()
        self._list_player.set_media_list(self._media_list)
        self._list_player.set_media_player(self._player.media_player_new())
        self._media_player = self._list_player.get_media_player()
        self._level = 0

    def play(self):
        self._list_player.play()
    def next(self):
        self._list_player.next()
    def pause(self):
        self._list_player.pause()
    def previous(self):
        self._list_player.previous()
    def stop(self):
        self._list_player.stop()
    def up(self, speed_change: float = None):
        self._media_player.set_rate(1 + (self._speed_change if(speed_change is None) else speed_change)/100)
        self._level += 1
    def down(self, speed_change: float = None):
        self._media_player.set_rate(1 - (self._speed_change if(speed_change is None) else speed_change)/100)
        self._level -= 1
    def get_level(self) -> int:
        return self._level
    