from attendances.tools.qr import generate_qr_code
from attendances.server import send
import pygame
import logging
import click
import json
import re


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
        return "\n".join(f'{str(person.id).rjust(3)} {person.name}' for person in context.attendances.people)


class RegisterAttendanceCommand(Command):
    @classmethod
    def create_cli_command(c):
        return _create_default_command_function(
            c.__name__,
            click.command(name='register'),
            click.argument('id', type=str)
        )

    def execute(self, context):
        id = self.id
        attendances = context.attendances
        if re.fullmatch(r'\d+', id):
            logging.info(f'Registering {id} as id')
            id = int(id)
            if attendances.person_exists(id):
                attendances.register(id)
                return f'Successfully registered {attendances.people[id].name}'
            else:
                return f'No one found with id={id}'
        else:
            logging.info(f'Registering {id} as name')
            regex = id
            people_with_name = attendances.find_people_by_name(regex)
            if len(people_with_name) == 1:
                person = people_with_name[0]
                if person.present.value:
                    return f'{person.name} is already registered'
                else:
                    person.register_attendance()
                    return f'Successfully registered {person.name}'
            elif len(people_with_name) > 1:
                names = "\n".join(person.name for person in people_with_name)
                return f'Error! Multiple matches found!\n{names}'
            else:
                return f'Error! No match found!'


class UnregisterAttendanceCommand(Command):
    @classmethod
    def create_cli_command(c):
        return _create_default_command_function(
            c.__name__,
            click.command(name='unregister'),
            click.argument('id', type=str)
        )

    def execute(self, context):
        id = self.id
        attendances = context.attendances
        if re.fullmatch(r'\d+', id):
            logging.info(f'Unregistering {id} as id')
            id = int(id)
            if attendances.person_exists(id):
                attendances.unregister(id)
                return f'Successfully unregistered {attendances.people[id].name}'
            else:
                return f'No one found with id={id}'
        else:
            logging.info(f'Unregistering {id} as name')
            regex = id
            people_with_name = attendances.find_people_by_name(regex)
            if len(people_with_name) == 1:
                person = people_with_name[0]
                if not person.present.value:
                    return f'{person.name} cannot be unregistered: they were never registered previously'
                else:
                    person.unregister_attendance()
                    return f'Successfully unregistered {person.name}'
            elif len(people_with_name) > 1:
                names = "\n".join(person.name for person in people_with_name)
                return f'Error! Multiple matches found!\n{names}'
            else:
                return f'Error! No match found!'


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
