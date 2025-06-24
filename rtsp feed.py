import cv2
import os
import nebulatk as ntk
from PIL import Image
from time import sleep, time
from threading import Thread
def close():
    cap.release()
    cv2.destroyAllWindows()
    quit()
window = ntk.Window(width = 16*50, height = 9*50, closing_command = close)


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
            
frame_container = ntk.Frame(window, width = 16*50, height = 9*50).place()


count = 0
cap = vcapture("rtsp://192.168.0.25:554/2") # hd rtsp stream 1, sd 2
cap.start()
img = ntk.image_manager.Image(path = None,_object = frame_container, image=None)

while(cap.running):
    frame_time1 = time()
    frame = cap.current_frame
    frame_time2 = time()
    #sleep(1/30)
    if frame is not None:
        #cv2.imshow('frame',frame)
        im = Image.fromarray(frame,"RGB")
        #print(im.size)
        img = ntk.image_manager.Image(path = None,_object = frame_container, image=im)
        img.resize(width = 16*50, height = 9*50)
        new_frame_container = ntk.Frame(window, width = 16*50, height = 9*50, image = img).place()
        frame_container.destroy()
        frame_container = new_frame_container
        
    frame_time3 = time()
        
    '''if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    if cv2.waitKey(1) & 0xFF == ord('z'):
        print("screenshot")
        cv2.imwrite(os.path.join("I:/de333r_usbdrive/Camera controller", '%d.png') % count, frame)
        count+=1
'''
    #print(frame_time1, frame_time2-frame_time1, frame_time3-frame_time2)
'''
cap.release()
cv2.destroyAllWindows()
'''
