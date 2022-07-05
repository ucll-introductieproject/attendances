import cv2
from pyzbar.pyzbar import decode
from contextlib import contextmanager
import click
import chime
from absentees.settings import load_settings
from pathlib import Path
import json



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
@click.option('--theme', help=f"One of {', '.join(chime.themes())}", default='big-sur')
@click.option('--source', help='Index of video source', default=0, type=int)
@click.option('--quiet', is_flag=True, help='No sound')
@click.option('--wait', help='Milliseconds between polls', default=500, type=int)
@click.option('--ignore', help='Milliseconds during which to ignore repeat scans', default=1000, type=int)
def tui(theme, source, quiet, wait, ignore):
   import absentees.tui as tui
   tui.run(theme, source, quiet, wait, ignore)


@click.command()
def gui():
    import absentees.gui as gui
    gui.run()


@click.group()
def config():
    pass


@click.command()
def show():
    settings = load_settings(Path.home().joinpath('absentees.config.json'))
    print(json.dumps(settings.data, indent=4, sort_keys=True))


cli.add_command(tui)
cli.add_command(gui)
cli.add_command(config)
config.add_command(show)

if __name__ == '__main__':
    cli()
