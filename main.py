#!/usr/bin/env python3
"""Manage your Minecraft server"""
# pylint: disable=no-member,assignment-from-no-return

import curses
from props.errors import ReturnError
from props.cmps.main import Root
from props.component import Component
from props.data import ReturnType, Colors, status

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
        if ret in (ReturnType.BACK, ReturnType.OK, ReturnType.ERR_BACK):
            stack.pop()
            continue

        key = stdscr.getch()
        result = comp.handle_key(key, stdscr)

        if result == ReturnType.RETURN_TO_MAIN:
            while len(stack) != 1:
                stack.pop()

        if result == ReturnType.EXIT:
            break

        if result == ReturnType.BACK:
            stack.pop()

        if isinstance(result, Component):
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
