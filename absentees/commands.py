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
            send(json.dumps(data))
        return register

    def __init__(self, name):
        self.__name = name

    def execute(self, model):
        model.attendances.register(self.__name)


def enumerate_commands():
    return Command.__subclasses__()


def find_command_with_name(name):
    for command in enumerate_commands():
        if command.__name__ == name:
            return command
    return None
