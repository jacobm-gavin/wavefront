"""Wavefront entry point."""

import argparse
import curses
import time

from rich.console import Console

from .model import Library, Track
from .providers import YtDlpSoundCloudSearch
from .ui import demo, draw, render


TRACKS = [
    Track("Midnight City", "M83", "Hurry Up, We're Dreaming", "7:03"),
    Track("Archangel", "Burial", "Untrue", "3:57"),
    Track("Innerbloom", "RÜFÜS DU SOL", "Bloom", "9:37"),
    Track("A Walk", "Tycho", "Dive", "5:17"),
    Track("Loud Places", "Jamie xx", "In Colour", "4:43"),
    Track("Night Drive", "Chromatics", "Kill for Love", "6:05"),
]


def run(stdscr) -> None:
    curses.curs_set(0)
    stdscr.nodelay(False)
    library = Library(TRACKS)
    selected = 0
    query = ""
    while True:
        draw(stdscr, library, selected, query)
        key = stdscr.get_wch()
        if key in ("Q", "\x1b"):
            return
        if key in (curses.KEY_DOWN, "j"):
            selected = min(selected + 1, max(0, len(library.search(query)) - 1))
        elif key in (curses.KEY_UP, "k"):
            selected = max(0, selected - 1)
        elif key in ("q", "Q"):
            tracks = library.search(query)
            if tracks:
                library.toggle_queue(tracks[selected])
        elif key == "/":
            # Keep the draft intentionally simple; a full input widget lands next.
            query = ""
        time.sleep(0.02)


def main() -> None:
    parser = argparse.ArgumentParser(description="A calmer SoundCloud-first terminal player")
    parser.add_argument("--demo", action="store_true", help="render a static preview")
    parser.add_argument("--search", metavar="QUERY", help="search SoundCloud with yt-dlp")
    args = parser.parse_args()
    if args.demo:
        demo()
    elif args.search is not None:
        try:
            tracks = YtDlpSoundCloudSearch().search(args.search)
        except RuntimeError as exc:
            parser.error(str(exc))
        Console().print(render(Library(tracks)))
    else:
        curses.wrapper(run)


if __name__ == "__main__":
    main()
