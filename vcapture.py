from threading import Thread
import cv2


class vcapture(Thread):
    def __init__(self, target):
        super().__init__()

        self.cap = cv2.VideoCapture(target)
        self.current_frame = None
        self.running = True

    def run(self):
        while self.cap.isOpened():
            ret, frame = self.cap.read()
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self.current_frame = frame
        self.running = False

    def release(self):
        self.cap.release()
