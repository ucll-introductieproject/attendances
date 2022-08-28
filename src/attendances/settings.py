def screen_size():
    import pygame
    info = pygame.display.Info()
    return (info.current_w, info.current_h)

frame_size = (640, 480)

window_size = (1920, 1080)

registration_file = 'attendances.txt'

sound_theme = 'big-sur'

quiet = False

qr_transformations = [
    # 'original',
    # 'grayscale',
    # 'bw',
    'bw_mean',
    # 'bw_gaussian',
]

frame_rate = 0

show_fps = True

analyze_every_n_frames = 5
