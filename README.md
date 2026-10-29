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

This is intentionally a UI draft: the next slice is a real input/search widget and a SoundCloud adapter backed by the existing `yt-dlp` workflow, without bypassing protected streams or DRM.

## Design direction

The visual language is dark, low-chrome, and slightly editorial instead of retro-skinned. The key change is context: library and queue are always close, while playback controls stay compact. The model is provider-neutral so SoundCloud can be first-class without making the rest of the player SoundCloud-specific.

## Tests

```sh
.venv/bin/pytest -q
```
