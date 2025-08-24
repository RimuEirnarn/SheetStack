"""App help component"""

# pylint: disable=no-member

import curses

from ..config import APP_CONFIG, APP_DIR
from ..data import ReturnType
from ..component import Component


class Help(Component):
    """Help component"""

    def __init__(self) -> None:
        super().__init__()
        self._key_events = {curses.KEY_LEFT: lambda: ReturnType.BACK}
        self._keystrokes = [
            ("[LEFT]", "Go back"),
            ("[RIGHT]", "Choose selected entry"),
            ("[ENTER]", "Choose selected entry"),
            ("[UP]", "Move selection up"),
            ("[DOWN]", "Move selection down"),
            ("[Q]", "Quit"),
        ]

    def draw(self, stdscr: curses.window):
        stdscr.addstr(
            0,
            0,
            "You can install PaperMC, select the default version, or run the server.",
        )
        stdscr.addstr(1, 0, "Use [LEFT] to go back.")

        stdscr.addstr(
            3,
            0,
            (
                "Did you know? The shell options returns you to your shell, "
                "directed at your server directory"
            ),
        )
        stdscr.addstr(
            4, 0, "Additionally, you can check your configuration, it's here:"
        )
        stdscr.addstr(5, 0, f"{APP_CONFIG}")
        stdscr.addstr(7, 0, "Wanna shortcut?")
        stdscr.addstr(8, 0, f"cd {APP_DIR}")

        stdscr.addstr(10, 0, "Keyboard shortcuts: ")
        for index, (key, label) in enumerate(self._keystrokes):
            stdscr.addstr(11 + index, 0, f"{key} -> {label}")
