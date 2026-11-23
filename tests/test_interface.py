from io import StringIO

import principale.interface as interface
from principale.interface import MENU_OPTIONS


def test_menu_contains_all_requested_numbered_actions():
    assert [number for number, _label in MENU_OPTIONS] == list(range(1, 15))


def test_begin_page_clears_content_and_redraws_constant_header(monkeypatch):
    events = []

    class FakeConsole:
        is_terminal = True

        def clear(self, *, home):
            events.append(("clear", home))

        def print(self, value):
            events.append(("title", value.plain))

    monkeypatch.setattr(interface, "console", FakeConsole())
    monkeypatch.setattr(interface, "show_banner", lambda *, animations: events.append(("header", animations)))

    interface.begin_page("Gestion des liens")

    assert events == [
        ("clear", True),
        ("header", False),
        ("title", "Gestion des liens"),
    ]


def test_full_screen_uses_and_restores_terminal_alternate_buffer(monkeypatch):
    output = StringIO()

    class FakeConsole:
        is_terminal = True
        file = output

    monkeypatch.setattr(interface, "console", FakeConsole())
    monkeypatch.setenv("TERM", "xterm-256color")

    with interface.full_screen():
        assert output.getvalue() == "\x1b[?1049h\x1b[3J\x1b[2J\x1b[H"

    assert output.getvalue().endswith("\x1b[?1049l")
