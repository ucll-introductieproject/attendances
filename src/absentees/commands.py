from absentees.server import send
import logging
import pygame
import click
import json


def _create_default_command_function(name):
    def function(**kwargs):
        data = { "command": name, "args": kwargs }
        response = send(json.dumps(data))
        print(response)
    return function


class Command:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


class ListPeopleCommand(Command):
    @classmethod
    def create_cli_command(c):
        function = _create_default_command_function(c.__name__)
        function = click.command(name='list-people')(function)
        return function

    def execute(self, model):
        return "\n".join(model.attendances.names)


class RegisterAttendanceCommand(Command):
    @classmethod
    def create_cli_command(c):
        function = _create_default_command_function(c.__name__)
        function = click.argument('name', type=str)(function)
        function = click.command(name='register')(function)
        return function

    def execute(self, model):
        if self.name in model.attendances.names:
            model.attendances.register(self.name)
            return 'Success'
        else:
            return f'{self.name} unknown'


class InjectFrameCommand(Command):
    @classmethod
    def create_cli_command(c):
        function = _create_default_command_function(c.__name__)
        function = click.option('-n', '--count', type=int, default=10)(function)
        function = click.argument('path', type=str)(function)
        function = click.command(name='inject')(function)
        return function

    def execute(self, model):
        logging.debug('Checking if video capturer supports injection')
        if hasattr(model.video_capturer, 'inject'):
            logging.debug('Video capturer does indeed support injection')
            logging.debug(f'Loading image {self.path}')
            surface = pygame.image.load(self.path)
            logging.debug(f'Injecting image')
            model.video_capturer.inject(surface, self.count)
            return 'Success'
        else:
            return 'Failure: video capturer does not support frame injection :('


def enumerate_commands():
    return Command.__subclasses__()


def find_command_with_name(name):
    for command in enumerate_commands():
        if command.__name__ == name:
            return command
    return None
