"""Playback boundary: yt-dlp streams audio to a local player process."""

from enum import Enum
import subprocess

from .model import Track
from .providers import yt_dlp_executable


class PlaybackState(Enum):
    STOPPED = "stopped"
    PLAYING = "playing"


class YtDlpPlayer:
    def __init__(self, player_command: str = "ffplay"):
        self.player_command = player_command
        self._extractor = None
        self._player = None
        self.state = PlaybackState.STOPPED

    def play(self, track: Track) -> PlaybackState:
        if not track.url:
            raise ValueError("track has no playable URL")
        self.stop()
        extract_command = [
            yt_dlp_executable(), "-o", "-", "-f", "bestaudio/best", "--no-playlist", "-q", track.url,
        ]
        self._extractor = subprocess.Popen(extract_command, stdout=subprocess.PIPE)
        self._player = subprocess.Popen(
            [self.player_command, "-nodisp", "-autoexit", "-i", "-"],
            stdin=self._extractor.stdout,
        )
        self.state = PlaybackState.PLAYING
        return self.state

    def stop(self) -> PlaybackState:
        for process in (self._player, self._extractor):
            if process is not None and process.poll() is None:
                process.terminate()
        self._player = None
        self._extractor = None
        self.state = PlaybackState.STOPPED
        return self.state
