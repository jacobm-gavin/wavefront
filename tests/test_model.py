import pytest

from wavefront.model import Library, Track


def test_library_search_is_case_insensitive_and_keeps_relevance_order():
    library = Library([
        Track("Midnight City", "M83", "Hurry Up, We're Dreaming", "7:03"),
        Track("City Lights", "The 1975", "Notes", "4:12"),
        Track("Sunset", "M83", "Junk", "3:55"),
    ])

    assert [track.title for track in library.search("city")] == [
        "Midnight City",
        "City Lights",
    ]


def test_queue_toggle_adds_and_removes_a_track_without_duplicates():
    library = Library([Track("A", "Artist", "Album", "1:00")])
    track = library.tracks[0]

    library.toggle_queue(track)
    library.toggle_queue(track)

    assert library.queue == []


def test_progress_bar_clamps_at_the_edges():
    assert Library.progress_bar(4, 10, width=10) == "████░░░░░░"
    assert Library.progress_bar(99, 10, width=10) == "██████████"
    assert Library.progress_bar(-1, 10, width=10) == "░░░░░░░░░░"
