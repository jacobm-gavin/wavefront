# Wavefront

A visual refresh draft for a SoundCloud-first terminal player. It keeps the good CLIAMP-shaped ideas — provider adapters, a real queue, keyboard-first control, and a headless-friendly core — while giving the everyday screen a calmer information hierarchy:

- **Discover** is the primary surface, not a wall of controls.
- **Now Playing** stays visible with a readable progress treatment.
- **Up Next** makes queue state obvious.
- Search, queue, playback, and providers are designed as separable model concerns.
- SoundCloud is the first provider; playback integration is deliberately not faked in this draft.

## Preview

```sh
python -m venv .venv
.venv/bin/pip install -e .
.venv/bin/python -m wavefront --demo
```

The interactive shell is available with:

```sh
.venv/bin/python -m wavefront
```

This is intentionally a UI draft: the next slice is wiring the real provider and playback adapters into keyboard commands, without bypassing protected streams or DRM.

## Search and playback boundaries

SoundCloud search is now real: the optional `--search` command invokes the local `yt-dlp` executable with a bounded `ytsearch10:` query and maps its JSON output into the same testable `Track` model. Install yt-dlp separately when you want search:

```sh
.venv/bin/pip install yt-dlp
.venv/bin/python -m wavefront --search "ambient house"
```

Missing yt-dlp, non-zero subprocess exits, invalid JSON, empty results, and timeouts are reported explicitly; an empty search returns no results. Search does not bypass protected streams or DRM.

The playback adapter is also implemented behind `YtDlpPlayer`: it streams a track URL from yt-dlp into a local `ffplay` process using a no-playlist, best-audio command. It is deliberately not exercised by the demo and does not require audio hardware in tests. The current interactive screen does not yet bind search results or playback controls to this adapter; wiring those commands is the next UI slice.

## Design direction

The visual language is dark, low-chrome, and slightly editorial instead of retro-skinned. The key change is context: library and queue are always close, while playback controls stay compact. The model is provider-neutral so SoundCloud can be first-class without making the rest of the player SoundCloud-specific.

## Tests

```sh
.venv/bin/pytest -q
```
