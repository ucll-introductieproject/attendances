import cv2


class FaceDetector:
    def __init__(self):
         self.__classifier = cv2.CascadeClassifier(f'{cv2.data.haarcascades}haarcascade_frontalface_default.xml')

    def detect(self, image):
        return self.__classifier.detectMultiScale(image, scaleFactor=1.1, minNeighbors=5)
