import cv2
from pyzbar.pyzbar import decode
from contextlib import contextmanager
from time import sleep, monotonic
import click
import chime
from absentees.settings import load_settings
from pathlib import Path
import json


def now():
    return monotonic()


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
    def initialize():
        print('Initializing...')
        chime.theme(theme)

    def play_success_sound():
        if not quiet:
            chime.success()

    def scan():
        scanned = {}

        with video_capture(source) as read_frame:
            print('Ready to scan QR codes!')
            while True:
                for decoded in decode(read_frame()):
                    data = decoded.data.decode('utf-8')
                    if data not in scanned:
                        scanned[data] = now()
                        print(data)
                        play_success_sound()
                    else:
                        delta = now() - scanned[data]
                        if delta > ignore / 1000:
                            print(f'Already scanned {data}')

                sleep(wait / 1000)

    initialize()
    scan()


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
