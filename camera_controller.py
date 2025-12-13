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

import atexit
import win32api
import win32con
from time import sleep

# (close, logoff, shutdown)
def console_ctrl_handler(event):
    if event in (win32con.CTRL_CLOSE_EVENT, win32con.CTRL_LOGOFF_EVENT, win32con.CTRL_SHUTDOWN_EVENT):
        atexit._run_exitfuncs()
        return True
    return False

# Register the save function to be called on normal program exit
atexit.register(close)

win32api.SetConsoleCtrlHandler(console_ctrl_handler, True)

if __name__ == "__main__":
    window = ntk.Window(width = 300, height = 600, closing_command=close).place()
    
    PAN_SPEED = 7
    TILT_SPEED = 7
    
    ptz_cam = Camera(ip="192.168.0.126")
    
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

    zoom_in_btn = ntk.Button(window, text = "+", height =50, width = 50, command = lambda: ptz_cam.zoom("tele"), command_off = ptz_cam.zoom_stop).place(25,210)
    zoom_out_btn = ntk.Button(window, text = "-", height =50, width = 50, command = lambda: ptz_cam.zoom("wide"), command_off = ptz_cam.zoom_stop).place(75,210)
    
    focus_in_btn = ntk.Button(window, text = "+", height =50, width = 50, command = lambda: ptz_cam.focus("far"), command_off = ptz_cam.zoom_stop).place(175,210)
    focus_out_btn = ntk.Button(window, text = "-", height =50, width = 50, command = lambda: ptz_cam.focus("near"), command_off = ptz_cam.zoom_stop).place(225,210)

    
    
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

    set_btn = ntk.Button(window, text = "Set", mode="toggle", height = 25,width=40).place(0,275)
    def toggle_focus():
        if not af_btn.state:
            ptz_cam.focus_mode("manual")
        else:
            ptz_cam.focus_mode("auto")
    
    af_btn = ntk.Button(window, text = "Autofocus", mode="toggle", height = 25,width=75, command=toggle_focus).place(225,275)
    if int(ptz_cam.inquire(ptz_cam.commands["inq"]["focus_mode"])[0]) == 2: 
        ntk.standard_methods.toggle_object_toggle(af_btn)
    
    def set_recall(index):
        if set_btn.state:
            ptz_cam.preset_set(index)
        else:
            ptz_cam.preset_recall(index)
    for i in range(0,9):
        y = 250 + 50*((i+3)//3)
        x_offset = 2 if (i+1)%3 == 0 else (i+1)%3-1
        x = 100*x_offset
        ntk.Button(window, text = f"{names[i]}", image = f"{img}{i+1}.jpg", text_color = "white", font=("Arial",9), height =50, width = 100, command = lambda i=i: set_recall(i+1)).place(x,y)
    
    
    frame_container = ntk.Frame(window, width=300, height=150).place(0,450)
    
    count = 0
    cap = vcapture("rtsp://192.168.0.126:554/2")  # hd rtsp stream 1, sd 2
    cap.start()
    img = ntk.image_manager.Image(_object=frame_container, image=None)
    
    while cap.running:
        try:
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
        except KeyboardInterrupt:
            close()
        
    
