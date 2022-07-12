from absentees.server import send
import click
import json


class Command:
    pass


class RegisterAttendanceCommand(Command):
    @classmethod
    def create_cli_command(c):
        @click.command()
        @click.argument('name', type=str)
        def register(**kwargs):
            data = { "command": c.__name__, "args": kwargs }
            response = send(json.dumps(data))
            print(response)
        return register

    def __init__(self, name):
        self.__name = name

    def execute(self, model):
        if self.__name in model.attendances.names:
            model.attendances.register(self.__name)
            return 'Success'
        else:
            return f'{self.__name} unknown'


def enumerate_commands():
    return Command.__subclasses__()


def find_command_with_name(name):
    for command in enumerate_commands():
        if command.__name__ == name:
            return command
    return None
