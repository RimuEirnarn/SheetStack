import curses
import os
import subprocess

def main(stdscr):
    curses.cbreak()
    stdscr.keypad(True)

    stdscr.addstr(0, 0, "Press 's' to open shell, 'q' to quit.")
    stdscr.refresh()

    while True:
        ch = stdscr.getch()
        if ch == ord('q'):
            break
        elif ch == ord('s'):
            # Tear down curses
            curses.endwin()

            # Run an interactive shell (bash/zsh/sh depending on env)
            shell = os.environ.get("SHELL", "/bin/sh")
            subprocess.call(shell)

            # Restore curses
            stdscr.refresh()
            curses.doupdate()
            stdscr.addstr(1, 0, "Returned from shell. Press 'q' to quit.")
            stdscr.refresh()

curses.wrapper(main)
