from wavefront.model import Library, Track
from wavefront.ui import draw


class FakeWindow:
    def __init__(self, rows=12, columns=60):
        self.rows = rows
        self.columns = columns
        self.operations = []

    def getmaxyx(self):
        return self.rows, self.columns

    def erase(self):
        self.operations.append(("erase",))

    def addnstr(self, row, column, text, count):
        self.operations.append(("addnstr", row, column, text, count))

    def refresh(self):
        self.operations.append(("refresh",))


def test_draw_clears_and_redraws_with_window_dimensions():
    window = FakeWindow(rows=8, columns=32)
    library = Library([Track("Night Drive", "DJ Test", "", "2:05")])

    draw(window, library)

    assert window.operations[0] == ("erase",)
    assert window.operations[-1] == ("refresh",)
    rows = [operation for operation in window.operations if operation[0] == "addnstr"]
    assert rows
    assert all(operation[1] < 8 and operation[4] == 32 for operation in rows)
    assert any("WAVEFRONT" in operation[3] for operation in rows)


def test_draw_does_not_write_past_a_narrow_terminal():
    window = FakeWindow(rows=5, columns=10)
    library = Library([Track("Night Drive", "DJ Test", "", "2:05")])

    draw(window, library)

    rows = [operation for operation in window.operations if operation[0] == "addnstr"]
    assert all(len(operation[3]) <= 10 for operation in rows)
