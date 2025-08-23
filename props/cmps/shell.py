"""Shell mode"""

# pylint: disable=no-member,no-name-in-module
from os import environ, chdir
from curses import window
from subprocess import call as subprocess

from props.curseutil import hide_system
from props.data import ReturnType
from props.config import SERVER_PATH
from ..component import Component

class Shell(Component):
    """Shell"""
    should_clear = False

    def draw(self, stdscr: window) -> None | ReturnType:
        with hide_system(stdscr):
            chdir(SERVER_PATH)
            returncode = subprocess(environ.get("SHELL", "/bin/sh"))
            input(f"\n[Return code {returncode}] Press enter to return to app... ")
        return ReturnType.OK
