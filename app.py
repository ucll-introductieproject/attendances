import cv2
from contextlib import contextmanager
import click
import absentees.settings
from pathlib import Path
import json


SETTINGS_PATH = Path.home().joinpath('absentees.config.json')


def load_settings():
    return absentees.settings.load_settings(SETTINGS_PATH)


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


@click.command()
def cameras():
    from absentees.capturer import Capturer
    for index, id in enumerate(Capturer.cameras()):
        print(f'[{index}] {id}')


cli.add_command(tui)
cli.add_command(gui)
cli.add_command(config)
cli.add_command(cameras)
config.add_command(config_show)
config.add_command(config_delete)

if __name__ == '__main__':
    cli()
