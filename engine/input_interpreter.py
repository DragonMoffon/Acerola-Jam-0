from typing import Any

from arcade.experimental.clock import Clock
from pyglet.math import Vec2

from engine.get_window import get_window


class InputType:
    """
    A device-agnostic input type. Input Interpreters send InputEvents to an InputBuffer to modify
     an InputType linked to a specific
    """

    def __init__(self, name: str, _initial_value: Any):
        self._name: str = ""
        self._last_time_updated: float = 0.0
        self._last_frame_update: int = 0

        self._poll_value: Any = _initial_value

        self._active: bool = False

    def activate(self):
        pass

    def deactivate(self):
        pass

    def update(self, value: Any, update_time: float, update_frame: int):
        raise NotImplementedError

    def poll(self) -> Any:
        raise NotImplementedError()


class DigitalInput(InputType):
    pass


class AnalogInput(InputType):
    # UNUSED
    pass


class AxisInput(InputType):
    pass


class InputEvent:
    pass


class InputInterpreter:
    pass


class KeyboardInterpreter:
    pass


class InputBuffer:
    pass
