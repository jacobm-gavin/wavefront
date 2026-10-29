"""Terminal rendering for the Wavefront draft."""

from io import StringIO

from rich.console import Console, Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from .model import Library, Track


ACCENT = "bright_cyan"
MUTED = "#718096"


def render(library: Library, selected: int = 0, query: str = "") -> Group:
    tracks = library.search(query)
    selected = max(0, min(selected, len(tracks) - 1)) if tracks else 0
    now = tracks[selected] if tracks else Track("Nothing found", "Try another search", "", "0:00")

    header = Text()
    header.append(" WAVEFRONT ", style="bold white on #17202a")
    header.append("  SOUNDCloud / LIBRARY", style=f"bold {ACCENT}")
    header.append("\n  A quieter player for the terminal", style=MUTED)

    table = Table(show_header=True, header_style=f"bold {ACCENT}", box=None, expand=True, padding=(0, 1))
    table.add_column("", width=3)
    table.add_column("TITLE", ratio=3)
    table.add_column("ARTIST", ratio=2)
    table.add_column("ALBUM", ratio=2)
    table.add_column("TIME", justify="right", width=7)
    for index, track in enumerate(tracks):
        marker = "▶" if index == selected else " "
        style = "bold white on #243447" if index == selected else "white"
        table.add_row(marker, track.title, track.artist, track.album, track.duration, style=style)

    queue = Text("QUEUE  ", style=f"bold {ACCENT}")
    queue.append(f"{len(library.queue)} tracks", style=MUTED)
    queue_lines = [queue]
    queue_lines.extend(Text(f"  {i + 1:02d}  {track.title}  ·  {track.artist}") for i, track in enumerate(library.queue[:4]))
    if not library.queue:
        queue_lines.append(Text("  Nothing queued yet — press q to add the selected track", style=MUTED))

    now_panel = Panel(
        Text.assemble(
            ("NOW PLAYING\n", f"bold {ACCENT}"),
            (f"{now.title}\n", "bold white"),
            (f"{now.artist}  ·  {now.album}\n\n", MUTED),
            ("  01:42  ", "white"),
            (Library.progress_bar(102, 243, 28), ACCENT),
            ("  04:03", MUTED),
        ),
        border_style=ACCENT,
        padding=(1, 2),
    )
    footer = Text("  / search    q queue    space play/pause    n next    ↑↓ move    ? shortcuts    esc quit", style=MUTED)
    return Group(header, Panel(table, title="DISCOVER", title_align="left", border_style="#2d4055"), now_panel, Panel(Text("\n".join(str(x) for x in queue_lines)), title="UP NEXT", border_style="#2d4055"), footer)


def draw(stdscr, library: Library, selected: int = 0, query: str = "") -> None:
    """Render one complete frame through the curses-owned terminal surface.

    Rich must render into a bounded buffer here rather than writing directly to
    ``/dev/tty``. Curses owns the screen in interactive mode; bypassing it
    leaves stale cells and lets Rich's width detection disagree with the
    curses window, which is especially visible under WSL.
    """
    rows, columns = stdscr.getmaxyx()
    columns = max(1, columns)
    console = Console(
        file=StringIO(),
        record=True,
        color_system=None,
        force_terminal=False,
        width=columns,
        height=max(1, rows),
    )
    console.print(render(library, selected, query))
    lines = console.export_text(styles=False, clear=False).splitlines()

    stdscr.erase()
    for row, line in enumerate(lines[: max(0, rows)]):
        stdscr.addnstr(row, 0, line[:columns], columns)
    stdscr.refresh()


def demo() -> None:
    tracks = [
        Track("Midnight City", "M83", "Hurry Up, We're Dreaming", "7:03"),
        Track("Archangel", "Burial", "Untrue", "3:57"),
        Track("Innerbloom", "RÜFÜS DU SOL", "Bloom", "9:37"),
        Track("A Walk", "Tycho", "Dive", "5:17"),
        Track("Loud Places", "Jamie xx", "In Colour", "4:43"),
        Track("Night Drive", "Chromatics", "Kill for Love", "6:05"),
    ]
    library = Library(tracks)
    library.toggle_queue(tracks[2])
    Console().print(render(library, selected=1))
