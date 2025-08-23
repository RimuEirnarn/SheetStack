"""Exit component"""

# pylint: disable=no-member,no-name-in-module

from curses import window
from ..component import Component

class Exit(Component):
    """Exit component"""

    def draw(self, _: window):
        return None
