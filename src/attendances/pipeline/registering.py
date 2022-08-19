class RegisteringNode:
    def __init__(self, attendances):
        self.__attendances = attendances

    def update_attendances(self, frame_analysis):
        for qr_code in frame_analysis.qr_codes:
            if self.__attendances.person_exists(qr_code):
                self.__attendances.register(qr_code)
