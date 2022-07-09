import pygame
import cv2


class FaceDetector:
    def __init__(self):
        xml_file = f'{cv2.data.haarcascades}haarcascade_frontalface_default.xml'
        self.__classifier = cv2.CascadeClassifier(xml_file)

    def detect(self, image):
        faces = self.__classifier.detectMultiScale(image, scaleFactor=1.1, minNeighbors=5)
        return [pygame.Rect(*face) for face in faces]
