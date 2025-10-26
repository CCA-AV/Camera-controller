import nebulatk as ntk
from controller import Camera


window = ntk.Window(width = 300, height = 600).place()

PAN_SPEED = 7
TILT_SPEED = 7

ptz_cam = Camera()

left_btn = ntk.Button(window, text = "<", height =50, width = 50, command = lambda: ptz_cam.pan_left(PAN_SPEED, TILT_SPEED), command_off = ptz_cam.pan_stop).place(75,100)
right_btn = ntk.Button(window, text = ">", height =50, width = 50, command = lambda: ptz_cam.pan_right(PAN_SPEED, TILT_SPEED), command_off = ptz_cam.pan_stop).place(175,100)

up_btn = ntk.Button(window, text = "^", height =50, width = 50, command = lambda: ptz_cam.pan_up(PAN_SPEED, TILT_SPEED), command_off = ptz_cam.pan_stop).place(125,50)
down_btn = ntk.Button(window, text = "v", height =50, width = 50, command = lambda: ptz_cam.pan_down(PAN_SPEED, TILT_SPEED), command_off = ptz_cam.pan_stop).place(125,150)


