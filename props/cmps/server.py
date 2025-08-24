"""Shell mode"""

# pylint: disable=no-member,no-name-in-module
from os import chdir, readlink, getcwd
from os.path import basename
from curses import window
from subprocess import call

from props.curseutil import hide_system
from props.data import ReturnType, status
from props.config import DEFAULT_PROFILE, DEFAULT_SYMLINK, read_config
from ..component import Component

class Server(Component):
    """Run active server"""

    should_clear = False

    def draw(self, stdscr: window) -> None | ReturnType:
        rt = -1
        current_dir = getcwd()
        config = read_config()
        with hide_system(stdscr):
            chdir(DEFAULT_PROFILE)
            link = readlink(DEFAULT_PROFILE)
            link_name = basename(link)
            server_name = basename(readlink(DEFAULT_SYMLINK)).replace('.jar', '')
            if not link_name == server_name:
                print("Mismatch in profile and server file link!")
                status.set("Server mismatch, please manage your server~")
                return ReturnType.ERR_BACK

            if not all(
                map(
                    lambda val: isinstance(val, (int, tuple)), config["memory"].values()
                )
            ):
                print(
                    "Invalid arguments for memory. Either min/max is not a valid number."
                )
                status.set("Invalid argument for memory. Please check your configuration")
                return ReturnType.ERR_BACK

            min_ram = f"{config['memory']['min']}G"
            max_ram = f"{config['memory']['max']}G"
            gui = "--gui" if config["gui"] else "--nogui"
            args = [
                config["java_path"],
                *config["additional_args"],
                f"-Xms{min_ram}",
                f"-Xmx{max_ram}",
                "-jar",
                "./server.jar",
                gui,
            ]
            print(f"Running Minecraft with this args:\n{' '.join(args)}")
            try:
                rt = call(args)
            except KeyboardInterrupt:
                print("Keyboard Interrupt (CTRL+C)!")
            except Exception as exc: # pylint: disable=broad-exception-caught
                print(f"Failed to run server: {exc}")
            input(f"\n[Return code {rt}] Press enter to return to app... ")
        chdir(current_dir)
        return ReturnType.BACK if rt == 0 else ReturnType.ERR_BACK
