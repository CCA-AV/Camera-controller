import nebulatk as ntk
from controller import Camera
from vcapture import vcapture
from time import sleep, time
from PIL import Image
import multiprocessing
import cv2

def close():
    if cap:
        cap.release()
    cv2.destroyAllWindows()
    quit()

if __name__ == "__main__":
    window = ntk.Window(width = 300, height = 600, closing_command=close).place()
    
    PAN_SPEED = 7
    TILT_SPEED = 7
    
    ptz_cam = Camera()
    
    left_btn = ntk.Button(window, text = "←", height =50, width = 50, command = lambda: ptz_cam.pan_left(PAN_SPEED, TILT_SPEED), command_off = ptz_cam.pan_stop).place(75,100)
    right_btn = ntk.Button(window, text = "→", height =50, width = 50, command = lambda: ptz_cam.pan_right(PAN_SPEED, TILT_SPEED), command_off = ptz_cam.pan_stop).place(175,100)
    
    left_btn = ntk.Button(window, text = "←", height =50, width = 50, command = lambda: ptz_cam.pan_left(PAN_SPEED*2, TILT_SPEED*2), command_off = ptz_cam.pan_stop).place(25,100)
    right_btn = ntk.Button(window, text = "→", height =50, width = 50, command = lambda: ptz_cam.pan_right(PAN_SPEED*2, TILT_SPEED*2), command_off = ptz_cam.pan_stop).place(225,100)
    
    up_btn = ntk.Button(window, text = "↑", height =50, width = 50, command = lambda: ptz_cam.pan_up(PAN_SPEED, TILT_SPEED), command_off = ptz_cam.pan_stop).place(125,50)
    down_btn = ntk.Button(window, text = "↓", height =50, width = 50, command = lambda: ptz_cam.pan_down(PAN_SPEED, TILT_SPEED), command_off = ptz_cam.pan_stop).place(125,150)
    
    
    up_left_btn = ntk.Button(window, text = "↖", height =50, width = 50, command = lambda: ptz_cam.pan_up_left(PAN_SPEED, TILT_SPEED), command_off = ptz_cam.pan_stop).place(75,50)
    up_right_btn = ntk.Button(window, text = "↗", height =50, width = 50, command = lambda: ptz_cam.pan_up_right(PAN_SPEED, TILT_SPEED), command_off = ptz_cam.pan_stop).place(175,50)
    
    
    down_left_btn = ntk.Button(window, text = "↙", height =50, width = 50, command = lambda: ptz_cam.pan_down_left(PAN_SPEED, TILT_SPEED), command_off = ptz_cam.pan_stop).place(75,150)
    down_right_btn = ntk.Button(window, text = "↘", height =50, width = 50, command = lambda: ptz_cam.pan_down_right(PAN_SPEED, TILT_SPEED), command_off = ptz_cam.pan_stop).place(175,150)
    
    names = [
        "Piano",
        "Stage Lyrics",
        "Speaker",
        "Announcements",
        "Stage no Lyrics",
        "Worship Leader",
        "Wide Shot Left",
        "Wide Shot Center",
        "Wide Shot Right"
    ]
    img="Images/"
    # Preset buttons
    for i in range(0,9):
        y = 250 + 50*((i+3)//3)
        x_offset = 2 if (i+1)%3 == 0 else (i+1)%3-1
        x = 100*x_offset
        ntk.Button(window, text = f"{names[i]}", image = f"{img}{i+1}.jpg", text_color = "white", font=("Arial",9), height =50, width = 100, command = lambda i=i: ptz_cam.preset_recall(i+1)).place(x,y)
    
    
    frame_container = ntk.Frame(window, width=300, height=150).place(0,450)
    
    count = 0
    cap = vcapture("rtsp://192.168.0.25:554/2")  # hd rtsp stream 1, sd 2
    cap.start()
    img = ntk.image_manager.Image(_object=frame_container, image=None)
    
    while cap.running:
        frame_time1 = time()
        frame = cap.current_frame
        frame_time2 = time()
        # sleep(1/30)
        sleep(1/24)
        if frame is not None:
            # cv2.imshow('frame',frame)
            im = Image.fromarray(frame, "RGB")
            # print(im.size)
            img = ntk.image_manager.Image(_object=frame_container, image=im)
            img.resize(width=300, height=150)
            new_frame_container = ntk.Frame(
                window, width=300, height=150, image=img
            ).place(0,450)
            frame_container.destroy()
            frame_container = new_frame_container
    
        frame_time3 = time()
        
    
