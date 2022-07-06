from pyzbar.pyzbar import decode
from collections import namedtuple


QRResult = namedtuple('QRResult', ['data', 'polygon'])


class QRScanner:
    def scan(self, image):
        return [self.__create_result(x) for x in decode(image)]

    def __create_result(self, decoded):
        data = decoded.data.decode('utf-8')
        polygon = [(p.x, p.y) for p in decoded.polygon]
        return QRResult(data, polygon)
