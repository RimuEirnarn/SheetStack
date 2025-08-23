"""Shell mode"""

# pylint: disable=no-member,no-name-in-module
from os import chdir, readlink
from os.path import basename
from curses import window
from subprocess import call as subprocess

from props.curseutil import hide_system
from props.data import ReturnType, status
from props.config import DEFAULT_PROFILE, DEFAULT_SYMLINK, CONFIG
from ..component import Component


class Server(Component):
    """Run active server"""

    should_clear = False

    def draw(self, stdscr: window) -> None | ReturnType:
        rt = -1
        with hide_system(stdscr):
            chdir(DEFAULT_PROFILE)
            link = readlink(DEFAULT_PROFILE)
            link_name = basename(link)
            server_name = basename(readlink(DEFAULT_SYMLINK)).replace('.jar', '')
            if not link_name == server_name:
                print("Mismatch in profile and server file link!")
                status.set("Server mismatch, please manage your server~")
                return ReturnType.ERR

            if not all(
                map(
                    lambda val: isinstance(val, (int, tuple)), CONFIG["memory"].values()
                )
            ):
                print(
                    "Invalid arguments for memory. Either min/max is not a valid number."
                )
                status.set("Invalid argument for memory. Please check your configuration")
                return ReturnType.ERR

            min_ram = f"{CONFIG['memory']['min']}G"
            max_ram = f"{CONFIG['memory']['max']}G"
            gui = "--gui" if CONFIG["gui"] else "--nogui"
            args = [
                "java",
                *CONFIG["additional_args"],
                f"-Xms{min_ram}",
                f"-Xmx{max_ram}",
                "-jar",
                "./server.jar",
                gui,
            ]
            print(f"Running Minecraft with this args:\n{' '.join(args)}")
            try:
                rt = subprocess(args)
            except KeyboardInterrupt:
                print("Keyboard Interrupt (CTRL+C)!")
            except Exception as exc: # pylint: disable=broad-exception-caught
                print(f"Failed to run server: {exc}")
            input(f"\n[Return code {rt}] Press enter to return to app... ")
        return ReturnType.OK if rt == 0 else ReturnType.ERR
