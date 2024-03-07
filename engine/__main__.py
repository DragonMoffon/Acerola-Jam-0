from pathlib import Path

from arcade.resources import add_resource_handle

from engine.application import launch_window


def main():
    add_resource_handle("r", Path("assets").resolve(strict=True))
    launch_window()


if __name__ == '__main__':
    main()
