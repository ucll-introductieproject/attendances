import logging


class RegisteringNode:
    def __init__(self, attendances):
        self.__attendances = attendances

    def update_attendances(self, frame_analysis):
        for qr_code in frame_analysis.qr_codes:
            id = qr_code.data
            if self.__attendances.person_exists(id):
                self.__attendances.register(id)
