import cv2
from contextlib import contextmanager
import click
import absentees.settings
from pathlib import Path
import json


SETTINGS_PATH = Path.home().joinpath('absentees.config.json')


def load_settings():
    return absentees.settings.load_settings(SETTINGS_PATH)


@contextmanager
def video_capture(source):
    def read_frame():
        _, frame = vc.read()
        return frame
    try:
        vc = cv2.VideoCapture(source)
        yield read_frame
    finally:
        vc.release()


@click.group()
def cli():
    pass


@click.command()
@click.option('--quiet', is_flag=True, help='No sound')
def tui(quiet):
   import absentees.tui as tui
   tui.run(load_settings(), quiet)


@click.command()
def gui():
    import absentees.gui as gui
    gui.run(load_settings())


@click.group()
def config():
    pass


@click.command('show')
def config_show():
    settings = load_settings()
    print(json.dumps(settings.data, indent=4, sort_keys=True))


@click.command('delete')
def config_delete():
    SETTINGS_PATH.unlink()


cli.add_command(tui)
cli.add_command(gui)
cli.add_command(config)
config.add_command(config_show)
config.add_command(config_delete)

if __name__ == '__main__':
    cli()
