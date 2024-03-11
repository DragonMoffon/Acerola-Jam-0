from typing import TypeGuard, TYPE_CHECKING

from arcade import get_window as _g_w

if TYPE_CHECKING:
    from engine.application import App


def get_window() -> "App":
    win: "App" = _g_w()
    return win
