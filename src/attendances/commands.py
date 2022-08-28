from attendances.tools.qr import generate_qr_code
from attendances.server import send
import pygame
import logging
import click
import json


class Context:
    def __init__(self, *, capturer, attendances):
        self.capturer = capturer
        self.attendances = attendances


def _create_default_command_function(name, *decorators):
    def function(**kwargs):
        data = { "command": name, "args": kwargs }
        response = send(json.dumps(data))
        print(response)

    for decorator in reversed(decorators):
        function = decorator(function)
    return function


class Command:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


class ListPeopleCommand(Command):
    @classmethod
    def create_cli_command(c):
        return _create_default_command_function(
            c.__name__,
            click.command(name='list-people')
        )

    def execute(self, context):
        return "\n".join(context.attendances.names)


class RegisterAttendanceCommand(Command):
    @classmethod
    def create_cli_command(c):
        return _create_default_command_function(
            c.__name__,
            click.command(name='register'),
            click.argument('name', type=str)
        )

    def execute(self, context):
        if self.name in context.attendances.names:
            context.attendances.register(self.name)
            return 'Success'
        else:
            return f'{self.name} unknown'


class InjectFrameCommand(Command):
    @classmethod
    def create_cli_command(c):
        return _create_default_command_function(
            c.__name__,
            click.command(name='inject'),
            click.argument('path', type=str),
            click.option('-n', '--count', type=int, default=10)
        )

    def execute(self, context):
        logging.debug('Checking if video capturer supports injection')
        if hasattr(context.capturer, 'inject'):
            logging.debug('Video capturer does indeed support injection')
            logging.debug(f'Loading image {self.path}')
            surface = pygame.image.load(self.path)
            logging.debug(f'Injecting image')
            context.capturer.inject(surface, self.count)
            return 'Success'
        else:
            return 'Failure: video capturer does not support frame injection :('


class InjectFrameCommand(Command):
    @classmethod
    def create_cli_command(c):
        return _create_default_command_function(
            c.__name__,
            click.command(name='inject-qr'),
            click.argument('data', type=str),
            click.option('-n', '--count', type=int, default=10)
        )

    def execute(self, context):
        logging.debug('Checking if video capturer supports injection')
        if hasattr(context.capturer, 'inject'):
            logging.debug('Video capturer does indeed support injection')
            logging.debug(f'Generating QR code')
            size = (640, 480)
            surface = generate_qr_code(self.data, size)
            logging.debug(f'Injecting image')
            context.capturer.inject(surface, self.count)
            return 'Success'
        else:
            return 'Failure: capturer does not support frame injection :('


def enumerate_commands():
    return Command.__subclasses__()


def find_command_with_name(name):
    for command in enumerate_commands():
        if command.__name__ == name:
            return command
    return None
