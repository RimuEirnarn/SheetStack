#!/usr/bin/env python3
"""Manage your Minecraft server"""
# pylint: disable=no-member,assignment-from-no-return

from os import chdir, environ, readlink, get_terminal_size
from os.path import basename
# import sys
from subprocess import call as subprocess
import curses
from time import sleep
from typing import Callable

from props.errors import ReturnError
from props.utility import supress, clear_info, windowed, prepare_windowed
from props.cmps.main import Root
from props.component import Component
from props.data import ReturnType, Colors, status
from props.osutils import (
    create_profile,
    create_symlink,
    list_versions,
    get_active_version,
)
from props.config import DEFAULT_PROFILE, DEFAULT_SYMLINK, PROFILE_DIR, SERVER_BIN, SERVER_PATH
from props.paper import fetch_global, fetch_version_info, fetch_minecraft
from props.typings import GlobalRepo, VersionBuildRepo
from props.curseutil import clear_line_yield, hide_system

# T = TypeVar("T")

COMMON_TEXT = (
    "Please install which version you wish to install"
    "(↑↓ to navigate, Enter to select, Left/Right to undo/select)"
)
BASE_HEIGHT = 2
RESERVED_LINES = 5
KEY_ENTER = 10

STATUS_INFO = {"0": " "}

@supress((ValueError,))
def select_build(stdscr: curses.window, version: str):
    """Select minecraft build"""
    clear_info()
    init = False
    data: VersionBuildRepo = {"builds": []}  # type: ignore
    selection = 0
    base_height = BASE_HEIGHT + 1
    while True:
        bottom = get_terminal_size().lines - 1
        stdscr.erase()
        if init is False:
            with clear_line_yield(stdscr, bottom):
                stdscr.addstr(bottom, 0, "Fetching build info...")
                data = fetch_version_info(version)
                init = True

        builds = tuple(reversed(data["builds"]))
        build = builds[selection]
        stdscr.addstr(0, 0, COMMON_TEXT)
        stdscr.addstr(
            1,
            0,
            (
                f"Selected: {version} / {build}. "
                "I recommend installing with newest build (usually with higher number)"
            ),
        )

        visible_rows = get_terminal_size().lines - RESERVED_LINES
        minln, maxln = prepare_windowed(selection, visible_rows)

        for idx, (rel_index, build_info) in enumerate(windowed(builds, minln, maxln)):
            style = 0
            if rel_index == selection:
                style = curses.color_pair(Colors.SELECTED)

            stdscr.addstr(base_height + idx, 0, f"-> {build_info}", style)

        key = stdscr.getch()
        if key == curses.KEY_UP and selection > 0:
            selection -= 1
        elif key == ord("q"):
            return ReturnType.EXIT
        elif key == curses.KEY_DOWN and selection < len(data["builds"]) - 1:
            selection += 1
        elif key == curses.KEY_LEFT:
            return ReturnType.BACK
        elif key in (curses.KEY_ENTER, KEY_ENTER, curses.KEY_RIGHT):
            with hide_system(stdscr):
                try:
                    print(f"Installing: PaperMC {version}/{build}")
                    fetch_minecraft(version, build)
                    STATUS_INFO["0"] = f"Installed Minecraft Paper {version}-{build}"
                    return ReturnType.RETURN_TO_MAIN
                except Exception as exc:  # pylint: disable=broad-exception-caught
                    STATUS_INFO["0"] = f"{type(exc).__name__}: {exc!s}"
                    return ReturnType.ERR


@supress([Exception])
def select_version_stage2(stdscr: curses.window, selected: str, data: GlobalRepo):
    """Select which minor version"""
    clear_info()
    verlist = tuple(filter(lambda ver: ver.startswith(selected), data["versions"]))

    selection = 0
    base_height = BASE_HEIGHT + 1
    while True:
        # height = curses.LINES
        stdscr.erase()
        stdscr.addstr(0, 0, COMMON_TEXT)
        stdscr.addstr(1, 0, f"Selected: {selected}")

        minln, maxln = prepare_windowed(selection, curses.LINES - RESERVED_LINES)

        for idx, (rel_index, version) in enumerate(windowed(verlist, minln, maxln)):
            style = 0
            if rel_index == selection:
                style = curses.color_pair(Colors.SELECTED)

            stdscr.addstr(base_height + idx, 0, f"-> {version}", style)

        key = stdscr.getch()
        if key == curses.KEY_UP and selection > 0:
            selection -= 1
        elif key == ord("q"):
            return ReturnType.EXIT
        elif key == curses.KEY_DOWN and selection < len(verlist) - 1:
            selection += 1
        elif key == curses.KEY_LEFT:
            return ReturnType.BACK
        elif key in (curses.KEY_ENTER, KEY_ENTER, curses.KEY_RIGHT):
            ret = select_build(stdscr, verlist[selection])
            if ret != ReturnType.BACK:
                return ret
            continue


@supress([Exception])
def select_version_stage1(stdscr: curses.window):
    """Select which major version"""
    clear_info()
    init = False
    data: GlobalRepo = {}  # type: ignore
    selection = 0

    while True:
        height = get_terminal_size().lines
        bottom = height - 1
        stdscr.erase()
        if init is False:
            with clear_line_yield(stdscr, bottom):
                stdscr.addstr(bottom, 0, "Fetching repository list...")
                stdscr.refresh()
                data = fetch_global()
            init = True
        stdscr.addstr(0, 0, COMMON_TEXT)

        minln, maxln = prepare_windowed(selection, curses.LINES - RESERVED_LINES)

        for idx, (rel_index, version) in enumerate(
            windowed(data["version_groups"], minln, maxln)
        ):
            style = 0
            if rel_index == selection:
                style = curses.color_pair(Colors.SELECTED)

            stdscr.addstr(BASE_HEIGHT + idx, 0, f"-> {version}", style)

        key = stdscr.getch()
        if key == curses.KEY_UP and selection > 0:
            selection -= 1
        elif key == ord("q"):
            return ReturnType.EXIT
        elif key == curses.KEY_DOWN and selection < len(data["version_groups"]) - 1:
            selection += 1
        elif key == curses.KEY_LEFT:
            return ReturnType.OK
        elif key in (curses.KEY_ENTER, KEY_ENTER, curses.KEY_RIGHT):
            ret = select_version_stage2(stdscr, data["version_groups"][selection], data)
            if ret != ReturnType.BACK:
                return ret
            continue


@supress([Exception])
def manage(stdscr: curses.window):
    clear_info()
    metadata = list_versions(str(SERVER_BIN))
    if metadata.type == ReturnType.ERR:
        STATUS_INFO["0"] = metadata.reason
        return ReturnType.ERR
    installed: list[str] = metadata.additional_info # type: ignore
    selection = 0
    while True:
        stdscr.erase()
        stdscr.addstr("Select Minecraft version to choose")

        minln, maxln = prepare_windowed(selection, curses.LINES - RESERVED_LINES)
        for idx, (rel_index, ver) in enumerate(windowed(installed, minln, maxln)):
            style = 0
            if rel_index == selection:
                style = curses.color_pair(Colors.SELECTED)
            stdscr.addstr(BASE_HEIGHT + idx, 0, f"-> {ver}", style)

        key = stdscr.getch()
        if key == curses.KEY_UP and selection > 0:
            selection -= 1
        elif key == ord("q"):
            return ReturnType.EXIT
        elif key == curses.KEY_DOWN and selection < len(installed) - 1:
            selection += 1
        elif key == curses.KEY_LEFT:
            return ReturnType.OK
        elif key in (curses.KEY_ENTER, KEY_ENTER, curses.KEY_RIGHT):
            ver = installed[selection]
            create_profile(installed[selection])
            create_symlink(str(PROFILE_DIR / ver.replace(".jar", "")),
                           str(DEFAULT_PROFILE))
            rt = create_symlink(str(SERVER_BIN / ver), str(DEFAULT_SYMLINK))
            STATUS_INFO["0"] = rt.reason
            return rt.type


@supress([Exception])
def run_server(stdscr: curses.window):
    """Run active/default server"""
    rt = -1
    with hide_system(stdscr):
        chdir(DEFAULT_PROFILE)
        link = readlink(DEFAULT_PROFILE)
        link_name = basename(link)
        server_name = basename(readlink(DEFAULT_SYMLINK))
        if not link_name in server_name:
            print("Mismatch in profile and server file link!")
            STATUS_INFO['0'] = "Server mismatch, please manage your server~"
            return ReturnType.ERR

        min_ram = "2G"
        max_ram = "4G"
        args = ['java', f'-Xms{min_ram}', f'-Xmx{max_ram}', '-jar', './server.jar', 'nogui']
        try:
            rt = subprocess(args)
        except KeyboardInterrupt:
            print("Keyboard Interrupt (CTRL+C)!")
        input(f"\n[Return code {rt}] Press enter to return to app... ")
    return ReturnType.OK

@supress([Exception])
def to_shell(stdscr: curses.window):
    """Return to shell"""
    with hide_system(stdscr):
        chdir(SERVER_PATH)
        returncode = subprocess(environ.get("SHELL", "/bin/sh"))
        input(f"\n[Return code {returncode}] Press enter to return to app... ")
    return ReturnType.OK

@supress([Exception])
def app_help(stdscr: curses.window):
    """App help"""
    while True:
        stdscr.erase()
        stdscr.addstr(
            0,
            0,
            "You can install PaperMC, select the default version, or run the server.",
        )
        stdscr.addstr(1, 0, "Use [Left] to go back.")

        key = stdscr.getch()
        if key == curses.KEY_LEFT:
            return ReturnType.BACK
        if key == ord("q"):
            return ReturnType.EXIT


@supress([Exception])
def app_exit(_: curses.window):
    """Exit from the app"""
    return ReturnType.EXIT


@supress([ValueError])
def halt5s(stdscr: curses.window):
    """Halt for 5 seconds"""
    clear_info()
    with clear_line_yield(stdscr, curses.LINES - 1):
        stdscr.addstr(curses.LINES - 1, 0, "Waiting...")
        stdscr.refresh()
        sleep(5)
    return ReturnType.OK


ENTRIES: list[tuple[str, Callable[[curses.window], ReturnType]]] = [
    ("Install new version", select_version_stage1),
    ("Select version", manage),
    ("Run", run_server),
    ("Shell", to_shell),
    ("Help", app_help),
    ("Halt 5s", halt5s),
    ("Exit", app_exit),
]


def app(stdscr: curses.window):
    """
    Interactive menu using curses with color support.
    Arrow keys navigate, Enter selects.
    """
    curses.curs_set(0)
    curses.start_color()
    curses.init_pair(
        Colors.SELECTED, curses.COLOR_BLACK, curses.COLOR_YELLOW
    )  # Selected
    curses.init_pair(Colors.ACTIVE, curses.COLOR_GREEN, curses.COLOR_BLACK)  # Active

    selected = 0
    key = 0
    base_height = BASE_HEIGHT + 1

    while True:
        # height = curses.LINES
        bottom = get_terminal_size().lines - 1
        version = get_active_version()
        stdscr.erase()
        stdscr.addstr(
            0,
            0,
            "Manage your Minecraft version (↑↓ to navigate, Enter/Right to select):",
        )
        if version:
            stdscr.addstr(1, 0, f"Current server version: {version}")
        stdscr.addstr(bottom, 0, STATUS_INFO["0"])

        for idx, (label, _) in enumerate(ENTRIES):
            style = 0
            if idx == selected:
                style = curses.color_pair(Colors.SELECTED)

            stdscr.addstr(base_height + idx, 0, f"-> {label}\n", style)

        # stdscr.addstr(height - 1, 0, "Hello!")
        key = stdscr.getch()

        if key == curses.KEY_UP and selected > 0:
            selected -= 1
        elif key == ord("q"):
            return
        elif key == curses.KEY_DOWN and selected < len(ENTRIES) - 1:
            selected += 1
        elif key in (curses.KEY_ENTER, KEY_ENTER, curses.KEY_RIGHT):
            return_type = ENTRIES[selected][1](stdscr)
            if return_type == ReturnType.EXIT:
                return

def runner(stdscr: curses.window):
    """Run the app, must be wrapped"""
    curses.curs_set(0)
    curses.start_color()
    curses.init_pair(
        Colors.SELECTED, curses.COLOR_BLACK, curses.COLOR_YELLOW
    )  # Selected
    curses.init_pair(Colors.ACTIVE, curses.COLOR_GREEN, curses.COLOR_BLACK)  # Active
    stack: list[Component] = [Root()]

    while stack:
        comp = stack[-1]
        if comp.should_init:
            comp.init(stdscr)

        if comp.should_clear:
            stdscr.erase()
        ret = comp.draw(stdscr)
        if ret in (ReturnType.BACK, ReturnType.OK):
            stack.pop()
            continue

        key = stdscr.getch()
        result = comp.handle_key(key, stdscr)

        if result == ReturnType.EXIT:
            break

        if result == ReturnType.BACK:
            stack.pop()
        elif isinstance(result, Component):
            try:
                stack.append(result)
            except ReturnError as exc:
                status.set(str(exc))
        # ReturnType.OK/ERR just continue

def main():
    """MC Server Manager (Paper)"""
    # curses.wrapper(app)
    curses.wrapper(runner)


if __name__ == "__main__":
    main()
