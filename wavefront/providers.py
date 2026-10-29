"""Legitimate SoundCloud search through the installed yt-dlp CLI."""

import json
import subprocess
import sys
from pathlib import Path
from typing import Any
import shutil

from .model import Track


def yt_dlp_executable() -> str:
    return shutil.which("yt-dlp") or str(Path(sys.executable).with_name("yt-dlp"))


def _duration(value: Any) -> str:
    if not isinstance(value, (int, float)) or value < 0:
        return "0:00"
    minutes, seconds = divmod(int(value), 60)
    return f"{minutes}:{seconds:02d}"


class YtDlpSoundCloudSearch:
    def __init__(self, timeout: float = 15, limit: int = 10):
        self.timeout = timeout
        self.limit = limit

    def search(self, query: str) -> list[Track]:
        if not query.strip():
            return []
        command = [
            yt_dlp_executable(), "--dump-single-json", "--flat-playlist", "--no-warnings",
            "--skip-download", f"ytsearch{self.limit}:{query}",
        ]
        try:
            result = subprocess.run(command, capture_output=True, text=True, timeout=self.timeout)
        except FileNotFoundError as exc:
            raise RuntimeError("yt-dlp is not installed; install it to search SoundCloud") from exc
        except subprocess.TimeoutExpired as exc:
            raise RuntimeError("yt-dlp search timed out") from exc
        if result.returncode:
            detail = (result.stderr or "").strip()
            raise RuntimeError(f"yt-dlp search failed{': ' + detail if detail else ''}")
        try:
            payload = json.loads(result.stdout)
        except json.JSONDecodeError as exc:
            raise RuntimeError("invalid yt-dlp output") from exc
        entries = payload.get("entries", []) if isinstance(payload, dict) else []
        if not isinstance(entries, list):
            raise RuntimeError("invalid yt-dlp output")
        return [self._track(entry) for entry in entries if isinstance(entry, dict) and entry.get("title")]

    @staticmethod
    def _track(entry: dict[str, Any]) -> Track:
        return Track(
            str(entry["title"]), str(entry.get("uploader") or entry.get("artist") or "Unknown artist"),
            str(entry.get("album") or ""), _duration(entry.get("duration")), "SoundCloud",
            str(entry.get("webpage_url") or entry.get("url") or ""),
        )
