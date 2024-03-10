from typing import TypeGuard

from arcade import get_window as _g_w

from engine.application import App


def get_window() -> App:
    win: TypeGuard[App] = get_window()
    return win
