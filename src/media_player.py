from vlc import Instance
import vlc
from typing import List
import time
from os.path import abspath, join, dirname
import librosa
from dataclasses import dataclass
import logging

logger = logging.getLogger(name="player")


@dataclass
class Song:
    song_path: str
    tempo: int


class Player:
    
    @classmethod
    def from_file(cls, path: str, speed_change: float = 5):
        """
        Create `Player` from playlist.txt file
        * `path`: Path to playlist.txt file
        * `speed_change`: amount of change to playback speed in percentage
        """
        path = abspath(path)
        logger.debug(f'Creating player from file {path}')
        with open(path, "r") as f:
            songs = f.read().splitlines()
            songs = [join(dirname(path), song) for song in songs] # Song paths in playlist.txt are relative to the playlist file
        return cls(songs=songs, speed_change=speed_change)

    def __init__(self, songs: List[str], speed_change: float = 5):
        """
        * `songs`: list of paths to songs playlist
        * `speed_change`: amount of change to playback speed in percentage
        """
        assert len(songs) != 0
        self._player = Instance("--loop")
        self._songs: List[Song] = []
        self._speed_change = speed_change
        self._media_list = self._player.media_list_new()
        self._current_song_idx = 0
        for song in songs:
            y, sr = librosa.load(song)
            tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
            self._songs.append(Song(song, tempo))
            self._media_list.add_media(self._player.media_new(song))

        self._list_player = self._player.media_list_player_new()
        self._list_player.set_media_list(self._media_list)
        self._list_player.set_media_player(self._player.media_player_new())
        self._media_player = self._list_player.get_media_player()
        self._level = 0

    @property
    def current_song(self):
        return self._songs[self._current_song_idx]

    def play(self):
        logger.debug('play')
        self._list_player.play()

    def next(self):
        logger.debug('next')
        self._list_player.next()
        if self._current_song_idx < len(self._songs):
            self._current_song_idx += 1

    def pause(self):
        logger.debug('pause')
        self._list_player.pause()

    def previous(self):
        logger.debug('previous')
        self._list_player.previous()
        if self._current_song_idx > 0:
            self._current_song_idx -= 1

    def stop(self):
        logger.debug('stop')
        self._list_player.stop()

    def up(self, speed_change: float = None):
        logger.debug('up')
        self._media_player.set_rate(
            1 + (self._speed_change if (speed_change is None) else speed_change) / 100
        )
        self._level += 1
        self.current_song.tempo += self.current_song.tempo * self._speed_change / 100

    def down(self, speed_change: float = None):
        logger.debug('down')
        self._media_player.set_rate(
            1 - (self._speed_change if (speed_change is None) else speed_change) / 100
        )
        self._level -= 1
        self.current_song.tempo -= self.current_song.tempo * self._speed_change / 100

    def get_level(self) -> int:
        return self._level

    def get_tempo(self) -> float:
        return self.current_song.tempo
