import cv2
from pyzbar.pyzbar import decode
from contextlib import contextmanager
from time import sleep
import click
import chime


@contextmanager
def video_capture(source):
    def read_frame():
        _, frame = vc.read()
        return frame
    try:
        vc = cv2.VideoCapture(source)
        yield read_frame
    finally:
        vc.release()



@click.command()
@click.option('--theme', help=f"One of {', '.join(chime.themes())}", default='big-sur')
@click.option('--source', help='Index of video source', default=0, type=int)
@click.option('--quiet', is_flag=True, help='No sound')
def main(theme, source, quiet):
    def play_success_sound():
        if not quiet:
            chime.success()

    print('Initializing...')
    chime.theme(theme)
    with video_capture(source) as read_frame:
        print('Ready to scan QR codes!')
        while True:
            decoded = decode(read_frame())
            if decoded:
                print(decoded)
                play_success_sound()
            sleep(0.5)



if __name__ == '__main__':
    main()
