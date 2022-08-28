import attendances.settings as settings


def load_data():
    with open(settings.students_file) as file:
        return [line.strip() for line in file]
