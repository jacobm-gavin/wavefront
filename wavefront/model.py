"""Wavefront: a calmer SoundCloud-first terminal player draft."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Track:
    title: str
    artist: str
    album: str
    duration: str
    source: str = "SoundCloud"


class Library:
    def __init__(self, tracks: list[Track]):
        self.tracks = tracks
        self.queue: list[Track] = []

    def search(self, query: str) -> list[Track]:
        needle = query.casefold().strip()
        if not needle:
            return list(self.tracks)

        # Keep library order stable so search never makes the cursor jump around.
        return [
            track
            for track in self.tracks
            if needle in f"{track.title} {track.artist} {track.album}".casefold()
        ]

    def toggle_queue(self, track: Track) -> None:
        if track in self.queue:
            self.queue.remove(track)
        else:
            self.queue.append(track)

    @staticmethod
    def progress_bar(position: int, total: int, width: int = 24) -> str:
        if total <= 0:
            filled = 0
        else:
            filled = round(max(0, min(position, total)) / total * width)
        return "█" * filled + "░" * (width - filled)
