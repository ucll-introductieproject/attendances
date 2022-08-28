def screen_size():
    import pygame
    info = pygame.display.Info()
    return (info.current_w, info.current_h)


registration_file = r'G:\repos\ucll\introproject\absentees\data\attendances.txt'

students_file = r'G:\repos\ucll\introproject\absentees\data\students.txt'

frame_size = (640, 480)

# Can also be set equal to screen_size() for fullscreen mode
window_size = (1920, 1080)

sound_theme = 'big-sur'

quiet = False

qr_transformations = [
    # 'original',
    # 'grayscale',
    'bw',
    # 'bw_mean',
    # 'bw_gaussian',
]

# 0 = no limit
frame_rate = 30

show_fps = True

# Lower = more responsive
# Higher = less computationally expensive
analyze_every_n_frames = 5
