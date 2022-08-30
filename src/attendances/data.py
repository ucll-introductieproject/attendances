from attendances.settings import settings
from attendances.model.attendances import Attendances


def load_data():
    with open(settings.students_file) as file:
        return [line.strip() for line in file]


def load_attendances():
    return Attendances(load_data())
