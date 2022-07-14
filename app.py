import logging
from absentees.sound import SoundPlayer
import click
import absentees.commands as commands
from absentees.settings import load_settings, default_settings
from pathlib import Path
import json
import socket


SETTINGS_PATH = Path.home().joinpath('absentees.config.json')


@click.group()
@click.option('-v', '--verbose', help='Verbose', is_flag=True)
@click.option('-q', '--quiet', help='Quiet', is_flag=True)
@click.option('--default', help='Use default settings', is_flag=True)
@click.pass_context
def cli(ctx, verbose, quiet, default):
    if verbose:
        logging.basicConfig(level=logging.DEBUG)

    ctx.ensure_object(dict)

    settings = default_settings() if default else load_settings(SETTINGS_PATH)

    if quiet:
        settings['sound.quiet'] = True

    ctx.obj['settings'] = settings



@click.command()
@click.pass_context
def tui(ctx):
   import absentees.tui as tui
   settings = ctx.obj['settings']
   sound_player = SoundPlayer(settings['sound.theme'], quiet=ctx.obj['quiet'])
   tui.run(settings, sound_player)

cli.add_command(tui)


@click.command()
@click.pass_context
def gui(ctx):
    import absentees.gui as gui
    settings = ctx.obj['settings']
    gui.run(settings)

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
    from absentees.capturer import Capturer
    for index, id in enumerate(Capturer.cameras()):
        print(f'[{index}] {id}')

cli.add_command(cameras)


@click.group()
def cmd():
    pass

cli.add_command(cmd)


for command_type in commands.enumerate_commands():
    create_command = getattr(command_type, 'create_cli_command')
    command = create_command()
    cmd.add_command(command)


if __name__ == '__main__':
    cli()
