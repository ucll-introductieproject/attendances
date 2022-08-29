from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

import logging
import click
import attendances.commands as commands
import attendances.data as data


@click.group()
@click.option('-v', '--verbose', help='Verbose', is_flag=True)
def cli(verbose):
    if verbose:
        logging.basicConfig(level=logging.DEBUG)
        logging.info('Turning on verbose mode')
    else:
        logging.basicConfig(level=logging.INFO)


@click.command()
def tui():
    """
    Simple text based UI
    """
    import attendances.tui as tui
    tui.run()

cli.add_command(tui)


@click.command()
def gui():
    """
    Run GUI
    """
    import attendances.gui as gui
    gui.run()

cli.add_command(gui)


@click.command()
def qrtest():
    """
    Test QR code detection with different transformations
    """
    import attendances.gui as gui
    gui.test_qr()

cli.add_command(qrtest)


@click.command()
def cameras():
    from attendances.tools.capturing import VideoCapturer
    for index, id in enumerate(VideoCapturer.cameras()):
        print(f'[{index}] {id}')

cli.add_command(cameras)


@click.group()
def cmd():
    """
    Send commands to TUI/GUI
    """
    pass

cli.add_command(cmd)


@click.command(name='generate-qr')
@click.argument('data', type=str)
@click.argument('path', type=str)
@click.option('-w', '--width', type=int)
@click.option('-h', '--height', type=int)
@click.option('-B', '--box-size', 'box_size', type=int, default=15)
@click.option('-b', '--border-size', 'border_size', type=int, default=0)
def generate_qr(data, path, width, height, box_size, border_size):
    """
    Generates a QR code and write its to file
    """
    from attendances.tools.qr import generate_qr_code
    import pygame
    surface = generate_qr_code(data, (width, height), box_size=box_size, border=border_size)
    pygame.image.save(surface, path)

cli.add_command(generate_qr)


@click.group()
def students():
    """
    Manipulate student data
    """
    pass

cli.add_command(students)


@click.command(name="list")
def list_students():
    names = data.load_data()
    for i, name in enumerate(names):
        print(f'{str(i + 1).rjust(3)} {name}')

students.add_command(list_students)


@click.group()
def excel():
    """
    Export to Excel sheet
    """
    pass

cli.add_command(excel)


@click.command(name="init")
@click.argument('filename')
def init_excel(filename):
    """
    Initialize new Excel sheet
    """
    from openpyxl import Workbook
    workbook = Workbook()
    sheet = workbook.active
    names = data.load_data()
    sheet['A1'] = 'id'
    sheet['B1'] = 'name'
    for id, name in enumerate(names):
        sheet[f'A{id+2}'] = id
        sheet[f'B{id+2}'] = name
    workbook.save(filename)

excel.add_command(init_excel)


for command_type in commands.enumerate_commands():
    create_command = getattr(command_type, 'create_cli_command')
    command = create_command()
    cmd.add_command(command)


if __name__ == '__main__':
    cli()
