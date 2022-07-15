from pyzbar.pyzbar import decode
from collections import namedtuple
import logging
import qrcode
import pygame


QRResult = namedtuple('QRResult', ['data', 'polygon'])


class QRScanner:
    def scan(self, image):
        return [self.__create_result(x) for x in decode(image)]

    def __create_result(self, decoded):
        data = decoded.data.decode('utf-8')
        polygon = [(p.x, p.y) for p in decoded.polygon]
        return QRResult(data, polygon)


def generate_qr_code(message, size, box_size=10, border=4):
    logging.debug('Creating QR image')
    qr = qrcode.QRCode(box_size=box_size, border=border)
    qr.add_data(message)
    image = qr.make_image().convert('RGB')

    logging.debug('Converting image to surface')
    image_surface = pygame.image.fromstring(image.tobytes(), image.size, image.mode)

    logging.debug('Centering QR code')
    result = pygame.Surface(size)
    result_width, result_height = size
    qr_width, qr_height = image_surface.get_size()
    x = (result_width - qr_width) / 2
    y = (result_height - qr_height) / 2
    result.blit(image_surface, (x, y))

    return result
