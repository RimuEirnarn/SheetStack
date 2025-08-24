"""Settings component"""

from curses import window
import curses
from props.data import ReturnType, status
from props.typings import Config
from props.config import read_config, write_config
from ..component import Component

SPECIAL_KEYS: list[int] = [
    value for key, value in curses.__dict__.items() if key.startswith("KEY")
]
KEY_ESC = 27
KEY_ENTER = 10
KEY_BACKSPACE = 127


class Settings(Component):
    """Edit manager configuration"""

    should_clear = True

    def __init__(self):
        super().__init__()
        self._select = 0
        config = read_config()
        self._config = config
        self._fields = [
            ("Path", config.get("path", "")),
            # ("Symlink", config.get("symlink_name", "server.jar")),
            ("Min RAM (GB)", str(config["memory"].get("min", 1))),
            ("Max RAM (GB)", str(config["memory"].get("max", 2))),
            ("GUI", str(config.get("gui", False))),
            ("Additional args", " ".join(config.get("additional_args", []))),
            ("Java path", config.get("java_path", "java")),
            # ("Auto-restart", str(config.get("auto_restart", False))),
            # ("Log path", config.get("log_path", "./logs")),
            ("", ""),
            ("[Save]", ""),
            ("[Cancel]", ""),
        ]
        self._editing = False
        self._buffer = ""
        self._escdelay = curses.get_escdelay()
        self._cursor_line = 0
        self._cursor_line_limit = 0

    def enter_edit(self):
        """Enter edit mode"""
        curses.set_escdelay(1)
        curses.curs_set(2)

    def exit_edit(self):
        """Exit edit mode"""
        curses.set_escdelay(self._escdelay)
        curses.curs_set(0)

    def draw(self, stdscr: window):
        # h, w = self.term_size
        self.show_status(stdscr)
        stdscr.addstr(0, 0, "Application settings")
        if self._editing:
            stdscr.addstr(1, 0, "You're now editing.")
        for i, (label, value) in enumerate(self._fields):
            if not label:
                continue
            prefix = "→ " if i == self._select else "  "
            if self._editing and self._select == i:
                value = self._buffer
            line = (
                f"{prefix}{label}: {value}"
                if not label.startswith("[")
                else f"{prefix}{label}"
            )
            stdscr.addstr(i + self.generic_height, 2, line)
        if self._editing:
            stdscr.move(self._select + self.generic_height, self._cursor_line)
        stdscr.refresh()

    def handle_editing(self, key: int):
        """Handle editing"""
        # Editing mode
        if key in (curses.KEY_ENTER, KEY_ENTER):  # Enter = save
            self.exit_edit()
            label, _ = self._fields[self._select]
            self._fields[self._select] = (label, self._buffer.strip())
            self._editing = False
            return ReturnType.CONTINUE
        if key == KEY_ESC:  # ESC = cancel edit
            self.exit_edit()
            self._editing = False
            self._buffer = ""
            return ReturnType.CONTINUE
        if key in (curses.KEY_BACKSPACE, KEY_BACKSPACE):  # Backspace
            self._buffer = self._buffer[:-1]
            if self._cursor_line > self._cursor_line_limit:
                self._cursor_line -= 1
            return ReturnType.CONTINUE

        if key in SPECIAL_KEYS:
            return ReturnType.CONTINUE
        self._buffer += chr(key)
        self._cursor_line += 1
        return ReturnType.CONTINUE

    def move_up(self):
        """Move UP"""
        if self._select > 0:
            self._select -= 1
        if not self._fields[self._select][0]:
            self.move_up()
            return ReturnType.CONTINUE
        return ReturnType.CONTINUE

    def move_down(self):
        """Move DOWN"""
        if self._select < len(self._fields) - 1:
            self._select += 1
        if not self._fields[self._select][0]:
            self.move_down()
            return ReturnType.CONTINUE
        return ReturnType.CONTINUE

    def handle_key(self, key: int, _: window) -> ReturnType: # pylint: disable=too-many-return-statements
        if not self._editing:
            if key == curses.KEY_UP:  # UP
                return self.move_up()
            if key == curses.KEY_DOWN:  # DOWN
                return self.move_down()
            if key == ord(" "):  # toggle boolean
                label, val = self._fields[self._select]
                if val in ("True", "False"):
                    self._fields[self._select] = (
                        label,
                        "False" if val == "True" else "True",
                    )
            if key == curses.KEY_LEFT:
                return ReturnType.BACK
            if key in (curses.KEY_ENTER, KEY_ENTER, curses.KEY_RIGHT):  # Enter
                label, val = self._fields[self._select]
                if not label:
                    return ReturnType.CONTINUE
                if label.startswith("[Save]"):
                    return self.save_config()
                if label.startswith("[Cancel]"):
                    return ReturnType.BACK
                self.enter_edit()
                self._cursor_line = len(f"  {label}: {val}") + 2
                self._cursor_line_limit = self._cursor_line - 1
                self._editing = True
                self._buffer = val
            if key == ord("q"):
                return ReturnType.EXIT
        else:
            self.handle_editing(key)

        return ReturnType.CONTINUE

    def save_config(self) -> ReturnType:
        """Save changed config"""
        config: Config = self._config
        try:
            config["path"] = self._fields[0][1]
            # config["symlink_name"] = self.fields[1][1]
            config["memory"]["min"] = int(self._fields[1][1])
            config["memory"]["max"] = int(self._fields[2][1])
            config["gui"] = self._fields[3][1] == "True"
            config["additional_args"] = self._fields[4][1].split()
            config["java_path"] = self._fields[5][1]
            # config["auto_restart"] = self.fields[7][1] == "True"
            # config["log_path"] = self.fields[8][1]
            status.set("Config saved successfully.")
            write_config(config)
            return ReturnType.OK
        except Exception as e:  # pylint: disable=broad-exception-caught
            status.set(f"Error saving config: {type(e).__name__}: {e}")
            return ReturnType.ERR
