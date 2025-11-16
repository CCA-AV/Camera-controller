import nebulatk as ntk
from controller import Camera


window = ntk.Window(width = 300, height = 600).place()

PAN_SPEED = 7
TILT_SPEED = 7

ptz_cam = Camera()

left_btn = ntk.Button(window, text = "←", height =50, width = 50, command = lambda: ptz_cam.pan_left(PAN_SPEED, TILT_SPEED), command_off = ptz_cam.pan_stop).place(75,100)
right_btn = ntk.Button(window, text = "→", height =50, width = 50, command = lambda: ptz_cam.pan_right(PAN_SPEED, TILT_SPEED), command_off = ptz_cam.pan_stop).place(175,100)

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
    ntk.Button(window, text = f"{names[i]}", image = f"{img}{i+1}.jpg", text_color = "white", font=("Arial",9), height =50, width = 100, command = lambda: ptz_cam.preset_recall(i+1)).place(x,y)

