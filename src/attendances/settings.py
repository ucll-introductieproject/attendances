import logging
import os.path
import json
import sys


class _Settings:
    @property
    def __screen_size():
        import pygame
        info = pygame.display.Info()
        return (info.current_w, info.current_h)

    @property
    def config_file_path(self):
        return os.path.expanduser("~/attendances.config.json")

    @property
    def config_file_contents(self):
        if os.path.exists(self.config_file_path):
            with open(self.config_file_path) as file:
                return json.load(file)
        else:
            print("No config file found for this user!")
            print(f"Expected to find it at {self.config_file_path}")
            print('Use the "config create" command to create the file')
            sys.exit(-1)

    def create_config_file(self, data_path):
        logging.info(f'Creating {self.config_file_path}')
        with open(self.config_file_path, 'w') as file:
            absolute_data_path = os.path.abspath(data_path)
            logging.info(f'Setting data path to {absolute_data_path}')
            data = {'data': absolute_data_path}
            json.dump(data, file)

    @property
    def data_directory(self):
        return self.config_file_contents['data']

    @property
    def registration_file(self):
        return os.path.join(self.data_directory, 'attendances.txt')

    @property
    def students_file(self):
        return os.path.join(self.data_directory, 'students.txt')

    @property
    def frame_size(self):
        return (640, 480)

    @property
    def window_size(self):
        # return self.__screen_size()  # Full screen mode
        return (1920, 1080)

    @property
    def sound_theme(self):
        return 'big-sur'

    @property
    def quiet(self):
        return False

    @property
    def qr_transformations(self):
        return [
            # 'original',
            # 'grayscale',
            'bw',
            # 'bw_mean',
            # 'bw_gaussian',
        ]

    @property
    def frame_rate(self):
        # 0 = no limit
        return 30

    @property
    def show_fps(self):
        return True

    @property
    def analyze_every_n_frames(self):
        # Lower = more responsive
        # Higher = less computationally expensive
        return 5

    @property
    def attendances_grid_column_count(self):
        return 12

settings = _Settings()
