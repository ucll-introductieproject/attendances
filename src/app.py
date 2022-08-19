import logging
from unicodedata import name
import click
import json
import attendances.commands as commands
from attendances.sound import SoundPlayer
from attendances.settings import load_settings, default_settings
from attendances.tools.qr import generate_qr_code
from pathlib import Path


SETTINGS_PATH = Path.home().joinpath('absentees.config.json')


@click.group()
@click.option('-v', '--verbose', help='Verbose', is_flag=True)
@click.option('-q', '--quiet', help='Quiet', is_flag=True)
@click.option('--default', help='Use default settings', is_flag=True)
@click.pass_context
def cli(ctx, verbose, quiet, default):
    if verbose:
        logging.basicConfig(level=logging.DEBUG)
        logging.info('Turning on verbose mode')
    else:
        logging.basicConfig(level=logging.INFO)

    ctx.ensure_object(dict)

    settings = default_settings() if default else load_settings(SETTINGS_PATH)

    if quiet:
        settings['sound.quiet'] = True

    ctx.obj['settings'] = settings



@click.command()
@click.pass_context
def tui(ctx):
    """
    Simple text based UI
    """
    import attendances.tui as tui
    settings = ctx.obj['settings']
    tui.run(settings)

cli.add_command(tui)


@click.command()
@click.pass_context
def gui(ctx):
    import attendances.gui as gui
    settings = ctx.obj['settings']
    gui.run(settings)

cli.add_command(gui)


@click.group()
def config():
    pass

cli.add_command(config)


@click.command('show')
@click.pass_context
def config_show(ctx):
    settings = ctx.obj['settings']
    print(json.dumps(settings.data, indent=4, sort_keys=True))

config.add_command(config_show)


@click.command('path')
def config_path():
    print(SETTINGS_PATH)

config.add_command(config_path)


@click.command('delete')
def config_delete():
    SETTINGS_PATH.unlink()

config.add_command(config_delete)


@click.command()
def cameras():
    from attendances.capturer import Capturer
    for index, id in enumerate(Capturer.cameras()):
        print(f'[{index}] {id}')

cli.add_command(cameras)


@click.group()
def cmd():
    pass

cli.add_command(cmd)


@click.command(name='generate-qr')
@click.argument('message', type=str)
@click.argument('path', type=str)
@click.pass_context
def generate_qr(ctx, message, path):
    import pygame
    settings = ctx.obj['settings']
    width = settings['video-capturing.width']
    height = settings['video-capturing.height']
    box_size = settings['qr.generation.box-size']
    border = settings['qr.generation.border']
    surface = generate_qr_code(message, (width, height), box_size=box_size, border=border)
    pygame.image.save(surface, path)

cli.add_command(generate_qr)


for command_type in commands.enumerate_commands():
    create_command = getattr(command_type, 'create_cli_command')
    command = create_command()
    cmd.add_command(command)


if __name__ == '__main__':
    cli()
