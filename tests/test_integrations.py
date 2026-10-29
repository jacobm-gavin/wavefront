import json
import subprocess

import pytest

from wavefront.model import Library, Track
from wavefront.playback import PlaybackState, YtDlpPlayer
from wavefront.providers import YtDlpSoundCloudSearch


def test_search_builds_yt_dlp_command_and_maps_results(monkeypatch):
    calls = []

    def fake_run(command, **kwargs):
        calls.append((command, kwargs))
        return subprocess.CompletedProcess(command, 0, json.dumps({
            "entries": [{
                "id": "abc123",
                "title": "Night Drive",
                "uploader": "DJ Test",
                "duration": 125,
                "webpage_url": "https://soundcloud.com/dj-test/night-drive",
            }],
        }))

    monkeypatch.setattr(subprocess, "run", fake_run)
    tracks = YtDlpSoundCloudSearch(timeout=7).search("night drive")

    assert tracks == [Track("Night Drive", "DJ Test", "", "2:05", "SoundCloud", "https://soundcloud.com/dj-test/night-drive")]
    assert calls[0][0][0].endswith("yt-dlp")
    assert calls[0][0][1:] == [
        "--dump-single-json", "--flat-playlist", "--no-warnings", "--skip-download", "ytsearch10:night drive",
    ]
    assert calls[0][1]["timeout"] == 7


def test_search_reports_missing_yt_dlp(monkeypatch):
    def missing(*args, **kwargs):
        raise FileNotFoundError

    monkeypatch.setattr(subprocess, "run", missing)
    with pytest.raises(RuntimeError, match="yt-dlp is not installed"):
        YtDlpSoundCloudSearch().search("ambient")


def test_search_handles_bad_output_and_process_failures(monkeypatch):
    monkeypatch.setattr(
        subprocess, "run",
        lambda *args, **kwargs: subprocess.CompletedProcess(args[0], 1, "", "network failed"),
    )
    with pytest.raises(RuntimeError, match="yt-dlp search failed"):
        YtDlpSoundCloudSearch().search("ambient")

    monkeypatch.setattr(
        subprocess, "run",
        lambda *args, **kwargs: subprocess.CompletedProcess(args[0], 0, "not json"),
    )
    with pytest.raises(RuntimeError, match="invalid yt-dlp output"):
        YtDlpSoundCloudSearch().search("ambient")


def test_search_handles_timeout_and_empty_results(monkeypatch):
    def timed_out(*args, **kwargs):
        raise subprocess.TimeoutExpired(args[0], kwargs["timeout"])

    monkeypatch.setattr(subprocess, "run", timed_out)
    with pytest.raises(RuntimeError, match="timed out"):
        YtDlpSoundCloudSearch().search("ambient")

    monkeypatch.setattr(
        subprocess, "run",
        lambda *args, **kwargs: subprocess.CompletedProcess(args[0], 0, json.dumps({"entries": []})),
    )
    assert YtDlpSoundCloudSearch().search("ambient") == []


def test_player_constructs_safe_command_without_network_or_audio(monkeypatch):
    calls = []

    class FakeProcess:
        def poll(self):
            return None

        def terminate(self):
            calls.append("terminate")

    class FakeYtProcess(FakeProcess):
        stdout = object()

    def fake_popen(command, **kwargs):
        calls.append((command, kwargs))
        return FakeYtProcess() if command[0].endswith("yt-dlp") else FakeProcess()

    monkeypatch.setattr("wavefront.playback.subprocess.Popen", fake_popen)
    track = Track("Night Drive", "DJ Test", "", "2:05", "SoundCloud", "https://soundcloud.com/dj-test/night-drive")
    player = YtDlpPlayer(player_command="ffplay")

    assert player.play(track) is PlaybackState.PLAYING
    assert calls[0][0][0].endswith("yt-dlp")
    assert calls[0][0][1:] == [
        "-o", "-", "-f", "bestaudio/best", "--no-playlist", "-q",
        "https://soundcloud.com/dj-test/night-drive",
    ]
    assert calls[1][0] == ["ffplay", "-nodisp", "-autoexit", "-i", "-"]
    assert player.state is PlaybackState.PLAYING
    assert player.stop() is PlaybackState.STOPPED
    assert calls[-1] == "terminate"


def test_library_can_load_provider_results_and_select_current_track():
    library = Library([])
    track = Track("Night Drive", "DJ Test", "", "2:05")

    library.replace_tracks([track])
    library.select(0)

    assert library.tracks == [track]
    assert library.selected == 0
    assert library.current == track
