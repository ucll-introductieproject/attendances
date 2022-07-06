import logging
import click
import absentees.settings
from pathlib import Path
import json


SETTINGS_PATH = Path.home().joinpath('absentees.config.json')


def load_settings():
    return absentees.settings.load_settings(SETTINGS_PATH)


@click.group()
@click.option('-v', '--verbose', help='Verbose', is_flag=True)
def cli(verbose):
    if verbose:
        logging.basicConfig(level=logging.DEBUG)


@click.command()
@click.option('--quiet', is_flag=True, help='No sound')
def tui(quiet):
   import absentees.tui as tui
   tui.run(load_settings(), quiet)

cli.add_command(tui)


@click.command()
def gui():
    import absentees.gui as gui
    gui.run(load_settings())

cli.add_command(gui)


@click.group()
def config():
    pass

cli.add_command(config)


@click.command('show')
def config_show():
    settings = load_settings()
    print(json.dumps(settings.data, indent=4, sort_keys=True))

config.add_command(config_show)


@click.command('delete')
def config_delete():
    SETTINGS_PATH.unlink()

config.add_command(config_delete)


@click.command()
def cameras():
    from absentees.capturer import Capturer
    for index, id in enumerate(Capturer.cameras()):
        print(f'[{index}] {id}')

cli.add_command(cameras)


if __name__ == '__main__':
    cli()
