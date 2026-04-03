import json
import threading
import time
from http import server
from socketserver import ThreadingMixIn

import cv2
import numpy as np


HOST = "127.0.0.1"
PORT = 8765
STREAM_PATH = "/stream.mjpg"
STATS_PATH = "/stats.json"

PAN_TILT_UNITS_PER_SPEED = 900.0
ZOOM_STD_UNITS_PER_SEC = 280000.0
ZOOM_VAR_UNITS_PER_SPEED = 70000.0
FOCUS_STD_UNITS_PER_SEC = 120.0
FOCUS_VAR_UNITS_PER_SPEED = 28.0
MOTION_TICK_S = 0.05


class _SimulatorState:
    def __init__(self):
        self.lock = threading.Lock()
        self.power = 1
        self.focus_mode = 2  # 2 auto, 3 manual
        self.backlight = 3  # 2 on, 3 off
        self.zoom_pos = 0
        self.focus_pos = 0
        self.pan_pos = 0x8000
        self.tilt_pos = 0x8000
        self.brightness = 128
        self.contrast = 128
        self.last_command = ""
        self.command_count = 0
        self.inquiry_count = 0
        self.client_count = 0
        self.started_at = time.time()
        self.presets = {}
        self.pan_velocity = 0.0
        self.tilt_velocity = 0.0
        self.zoom_velocity = 0.0
        self.focus_velocity = 0.0

    def snapshot(self):
        with self.lock:
            return {
                "power": self.power,
                "focus_mode": self.focus_mode,
                "backlight": self.backlight,
                "zoom_pos": self.zoom_pos,
                "focus_pos": self.focus_pos,
                "pan_pos": self.pan_pos,
                "tilt_pos": self.tilt_pos,
                "brightness": self.brightness,
                "contrast": self.contrast,
                "last_command": self.last_command,
                "command_count": self.command_count,
                "inquiry_count": self.inquiry_count,
                "client_count": self.client_count,
                "uptime_s": round(time.time() - self.started_at, 3),
                "pan_velocity": self.pan_velocity,
                "tilt_velocity": self.tilt_velocity,
                "zoom_velocity": self.zoom_velocity,
                "focus_velocity": self.focus_velocity,
            }

    def set_last_command(self, command_hex):
        with self.lock:
            self.last_command = command_hex
            self.command_count += 1

    def increment_inquiry(self):
        with self.lock:
            self.inquiry_count += 1


STATE = _SimulatorState()
_SERVER_LOCK = threading.Lock()
_SERVER_STARTED = False
_SERVER_INSTANCE = None
_MOTION_THREAD_STARTED = False
_MOTION_THREAD_LOCK = threading.Lock()


def _nibble_separated(value, nibbles):
    hex_value = f"{value:0{nibbles}x}"[-nibbles:]
    return "".join(f"0{char}" for char in hex_value)


def _reply_zoom():
    with STATE.lock:
        return f"9050{_nibble_separated(STATE.zoom_pos, 4)}ff"


def _reply_focus():
    with STATE.lock:
        return f"9050{_nibble_separated(STATE.focus_pos, 4)}ff"


def _reply_pan_tilt():
    with STATE.lock:
        pan = _nibble_separated(STATE.pan_pos, 4)
        tilt = _nibble_separated(STATE.tilt_pos, 4)
    return f"9050{pan}{tilt}ff"


def _reply_focus_mode():
    with STATE.lock:
        return f"9050{STATE.focus_mode:02x}ff"


def _reply_backlight():
    with STATE.lock:
        return f"9050{STATE.backlight:02x}ff"


def _reply_brightness():
    with STATE.lock:
        value = STATE.brightness & 0xFF
    return f"905000000{value >> 4:x}0{value & 0xF:x}ff"


def _reply_contrast():
    with STATE.lock:
        value = STATE.contrast & 0xFF
    return f"905000000{value >> 4:x}0{value & 0xF:x}ff"


def _reply_other_block():
    with STATE.lock:
        power_nibble = STATE.power & 0x1
        reverse_nibble = 0
        effect_nibble = 0
    return f"90500{power_nibble:x}0{reverse_nibble:x}000{effect_nibble:x}000000000000000000ff"


def _clamp(value, min_value, max_value):
    return max(min_value, min(max_value, value))


def _set_zoom_direct(command):
    value = int(command[8:16], 16)
    with STATE.lock:
        STATE.zoom_pos = _clamp(value, 0, 0x04000000)
        STATE.zoom_velocity = 0.0


def _set_focus_direct(command):
    nibbles = command[9:16:2]
    value = int("".join(nibbles), 16)
    with STATE.lock:
        STATE.focus_pos = _clamp(value, 0, 1770)
        STATE.focus_velocity = 0.0


def _set_pan_tilt_abs(command):
    pan_nibbles = command[13:20:2]
    tilt_nibbles = command[21:28:2]
    pan = int("".join(pan_nibbles), 16)
    tilt = int("".join(tilt_nibbles), 16)
    with STATE.lock:
        STATE.pan_pos = _clamp(pan, 0, 0xFFFF)
        STATE.tilt_pos = _clamp(tilt, 0, 0xFFFF)
        STATE.pan_velocity = 0.0
        STATE.tilt_velocity = 0.0


def _set_pan_tilt_rel(command):
    pan_nibbles = command[13:20:2]
    tilt_nibbles = command[21:28:2]
    pan_delta = int("".join(pan_nibbles), 16)
    tilt_delta = int("".join(tilt_nibbles), 16)
    with STATE.lock:
        STATE.pan_pos = _clamp(STATE.pan_pos + pan_delta, 0, 0xFFFF)
        STATE.tilt_pos = _clamp(STATE.tilt_pos + tilt_delta, 0, 0xFFFF)
        STATE.pan_velocity = 0.0
        STATE.tilt_velocity = 0.0


def _set_brightness(command):
    value = int(command[13] + command[15], 16)
    with STATE.lock:
        STATE.brightness = _clamp(value, 0, 255)


def _set_contrast(command):
    value = int(command[13] + command[15], 16)
    with STATE.lock:
        STATE.contrast = _clamp(value, 0, 255)


def _drive_pan_tilt(command):
    pan_speed = int(command[8:10], 16)
    tilt_speed = int(command[10:12], 16)
    pan_dir = int(command[12:14], 16)
    tilt_dir = int(command[14:16], 16)

    with STATE.lock:
        if pan_dir == 0x01:
            STATE.pan_velocity = -max(1, pan_speed) * PAN_TILT_UNITS_PER_SPEED
        elif pan_dir == 0x02:
            STATE.pan_velocity = max(1, pan_speed) * PAN_TILT_UNITS_PER_SPEED
        elif pan_dir == 0x03:
            STATE.pan_velocity = 0.0

        if tilt_dir == 0x01:
            STATE.tilt_velocity = -max(1, tilt_speed) * PAN_TILT_UNITS_PER_SPEED
        elif tilt_dir == 0x02:
            STATE.tilt_velocity = max(1, tilt_speed) * PAN_TILT_UNITS_PER_SPEED
        elif tilt_dir == 0x03:
            STATE.tilt_velocity = 0.0


def _set_preset(command):
    preset_num = int(command[10:12], 16)
    with STATE.lock:
        STATE.presets[preset_num] = (STATE.pan_pos, STATE.tilt_pos, STATE.zoom_pos, STATE.focus_pos)


def _recall_preset(command):
    preset_num = int(command[10:12], 16)
    with STATE.lock:
        if preset_num not in STATE.presets:
            return
        pan, tilt, zoom, focus = STATE.presets[preset_num]
        STATE.pan_pos = pan
        STATE.tilt_pos = tilt
        STATE.zoom_pos = zoom
        STATE.focus_pos = focus
        STATE.pan_velocity = 0.0
        STATE.tilt_velocity = 0.0
        STATE.zoom_velocity = 0.0
        STATE.focus_velocity = 0.0


def _set_zoom_velocity(velocity):
    with STATE.lock:
        STATE.zoom_velocity = velocity


def _set_focus_velocity(velocity):
    with STATE.lock:
        STATE.focus_velocity = velocity


def _apply_continuous_motion(dt):
    with STATE.lock:
        if STATE.pan_velocity != 0.0:
            STATE.pan_pos = _clamp(
                int(STATE.pan_pos + STATE.pan_velocity * dt), 0, 0xFFFF
            )
        if STATE.tilt_velocity != 0.0:
            STATE.tilt_pos = _clamp(
                int(STATE.tilt_pos + STATE.tilt_velocity * dt), 0, 0xFFFF
            )
        if STATE.zoom_velocity != 0.0:
            STATE.zoom_pos = _clamp(
                int(STATE.zoom_pos + STATE.zoom_velocity * dt), 0, 0x04000000
            )
        if STATE.focus_velocity != 0.0:
            STATE.focus_pos = _clamp(
                int(STATE.focus_pos + STATE.focus_velocity * dt), 0, 1770
            )


def _motion_worker():
    last_time = time.time()
    while True:
        now = time.time()
        _apply_continuous_motion(now - last_time)
        last_time = now
        time.sleep(MOTION_TICK_S)


def ensure_motion_thread():
    global _MOTION_THREAD_STARTED
    with _MOTION_THREAD_LOCK:
        if _MOTION_THREAD_STARTED:
            return
        thread = threading.Thread(
            target=_motion_worker, name="testcamera-motion", daemon=True
        )
        thread.start()
        _MOTION_THREAD_STARTED = True


INQUIRY_REPLIES = {
    "81090447ff": _reply_zoom,
    "81090448ff": _reply_focus,
    "81090612ff": _reply_pan_tilt,
    "81090438ff": _reply_focus_mode,
    "81090433ff": _reply_backlight,
    "810904a1ff": _reply_brightness,
    "810904a2ff": _reply_contrast,
    "81097e7e02ff": _reply_other_block,
}


def apply_visca_command(command_hex):
    command = command_hex.lower()
    if not command:
        return "9051ff"

    if command in INQUIRY_REPLIES:
        STATE.increment_inquiry()
        return INQUIRY_REPLIES[command]()

    STATE.set_last_command(command)
    if command == "8101040002ff":
        with STATE.lock:
            STATE.power = 1
    elif command == "8101040003ff":
        with STATE.lock:
            STATE.power = 0
            STATE.pan_velocity = 0.0
            STATE.tilt_velocity = 0.0
            STATE.zoom_velocity = 0.0
            STATE.focus_velocity = 0.0
    elif command == "8101043802ff":
        with STATE.lock:
            STATE.focus_mode = 2
    elif command == "8101043803ff":
        with STATE.lock:
            STATE.focus_mode = 3
    elif command.startswith("810104330") and command.endswith("ff"):
        value = int(command[9], 16)
        with STATE.lock:
            STATE.backlight = _clamp(value, 2, 3)
    elif command.startswith("81010447") and command.endswith("ff") and len(command) == 18:
        _set_zoom_direct(command)
    elif command == "8101040702ff":
        _set_zoom_velocity(ZOOM_STD_UNITS_PER_SEC)
    elif command == "8101040703ff":
        _set_zoom_velocity(-ZOOM_STD_UNITS_PER_SEC)
    elif command.startswith("810104072") and command.endswith("ff") and len(command) == 12:
        speed = max(1, int(command[9], 16))
        _set_zoom_velocity(speed * ZOOM_VAR_UNITS_PER_SPEED)
    elif command.startswith("810104073") and command.endswith("ff") and len(command) == 12:
        speed = max(1, int(command[9], 16))
        _set_zoom_velocity(-(speed * ZOOM_VAR_UNITS_PER_SPEED))
    elif command == "8101040700ff":
        _set_zoom_velocity(0.0)
    elif command.startswith("810104480") and command.endswith("ff") and len(command) == 18:
        _set_focus_direct(command)
    elif command == "8101040802ff":
        _set_focus_velocity(FOCUS_STD_UNITS_PER_SEC)
    elif command == "8101040803ff":
        _set_focus_velocity(-FOCUS_STD_UNITS_PER_SEC)
    elif command.startswith("810104082") and command.endswith("ff") and len(command) == 12:
        speed = max(1, int(command[9], 16))
        _set_focus_velocity(speed * FOCUS_VAR_UNITS_PER_SPEED)
    elif command.startswith("810104083") and command.endswith("ff") and len(command) == 12:
        speed = max(1, int(command[9], 16))
        _set_focus_velocity(-(speed * FOCUS_VAR_UNITS_PER_SPEED))
    elif command == "8101040800ff":
        _set_focus_velocity(0.0)
    elif command.startswith("81010602") and command.endswith("ff") and len(command) == 30:
        _set_pan_tilt_abs(command)
    elif command.startswith("81010603") and command.endswith("ff") and len(command) == 30:
        _set_pan_tilt_rel(command)
    elif command.startswith("81010601") and command.endswith("ff") and len(command) == 18:
        _drive_pan_tilt(command)
    elif command == "8101043810ff":
        with STATE.lock:
            STATE.focus_mode = 3 if STATE.focus_mode == 2 else 2
    elif command.startswith("8101043f01") and command.endswith("ff") and len(command) == 14:
        _set_preset(command)
    elif command.startswith("8101043f02") and command.endswith("ff") and len(command) == 14:
        _recall_preset(command)
    elif command.startswith("810104a100000") and command.endswith("ff"):
        _set_brightness(command)
    elif command.startswith("810104a200000") and command.endswith("ff"):
        _set_contrast(command)

    return "9051ff"


def _build_frame():
    with STATE.lock:
        zoom_pos = STATE.zoom_pos
        focus_pos = STATE.focus_pos
        pan_pos = STATE.pan_pos
        tilt_pos = STATE.tilt_pos
        focus_mode = STATE.focus_mode

    width = 960
    height = 540
    frame = np.zeros((height, width, 3), dtype=np.uint8)
    frame[:] = (18, 22, 30)

    for x in range(0, width, 60):
        cv2.line(frame, (x, 0), (x, height), (45, 50, 65), 1)
    for y in range(0, height, 60):
        cv2.line(frame, (0, y), (width, y), (45, 50, 65), 1)

    now = time.strftime("%H:%M:%S")
    cv2.putText(
        frame,
        "Test Camera Simulator",
        (30, 60),
        cv2.FONT_HERSHEY_SIMPLEX,
        1.1,
        (0, 210, 255),
        2,
        cv2.LINE_AA,
    )
    cv2.putText(
        frame,
        f"Time: {now}",
        (30, 105),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.9,
        (200, 230, 255),
        2,
        cv2.LINE_AA,
    )

    center_x = int((pan_pos / 0xFFFF) * width)
    center_y = int((tilt_pos / 0xFFFF) * height)
    cv2.circle(frame, (center_x, center_y), 20, (40, 220, 80), -1)
    cv2.putText(
        frame,
        "PT",
        (center_x - 15, center_y + 6),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (10, 30, 10),
        2,
        cv2.LINE_AA,
    )

    zoom_factor = 1.0 + (zoom_pos / 0x04000000) * 3.0
    crop_w = max(int(width / zoom_factor), 120)
    crop_h = max(int(height / zoom_factor), 80)
    ox = _clamp(center_x - crop_w // 2, 0, width - crop_w)
    oy = _clamp(center_y - crop_h // 2, 0, height - crop_h)
    frame = frame[oy : oy + crop_h, ox : ox + crop_w]
    frame = cv2.resize(frame, (width, height), interpolation=cv2.INTER_LINEAR)

    blur_scale = int((focus_pos / 1770) * 8)
    kernel = max(1, 1 + 2 * blur_scale)
    if kernel > 1:
        frame = cv2.GaussianBlur(frame, (kernel, kernel), 0)

    cv2.putText(
        frame,
        f"Zoom:{zoom_pos} Focus:{focus_pos} Mode:{'AF' if focus_mode == 2 else 'MF'}",
        (20, height - 24),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2,
        cv2.LINE_AA,
    )
    return frame


class _ThreadedHTTPServer(ThreadingMixIn, server.HTTPServer):
    daemon_threads = True


class _SimulatorRequestHandler(server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self._serve_dashboard()
            return
        if self.path.startswith(STATS_PATH):
            self._serve_stats()
            return
        if self.path.startswith(STREAM_PATH):
            self._serve_stream()
            return
        self.send_error(404, "Not found")

    def _serve_dashboard(self):
        body = """<!doctype html>
<html>
<head>
<meta charset="utf-8" />
<title>Test Camera Simulator</title>
<style>
body { font-family: Segoe UI, sans-serif; margin: 24px; background: #141822; color: #e7ecff; }
h1 { margin: 0 0 12px 0; }
.layout { display: flex; gap: 20px; align-items: flex-start; }
img { width: 720px; border: 1px solid #39425d; border-radius: 6px; }
pre { margin: 0; background: #0f1320; border: 1px solid #39425d; border-radius: 6px; padding: 12px; min-width: 320px; }
</style>
</head>
<body>
<h1>Test Camera Simulator</h1>
<div class="layout">
  <img src="/stream.mjpg" />
  <pre id="stats">loading...</pre>
</div>
<script>
async function refreshStats() {
  const res = await fetch('/stats.json');
  const data = await res.json();
  document.getElementById('stats').textContent = JSON.stringify(data, null, 2);
}
setInterval(refreshStats, 700);
refreshStats();
</script>
</body>
</html>"""
        data = body.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _serve_stats(self):
        payload = json.dumps(STATE.snapshot()).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def _serve_stream(self):
        with STATE.lock:
            STATE.client_count += 1
        boundary = "frame"
        self.send_response(200)
        self.send_header(
            "Content-Type", f"multipart/x-mixed-replace; boundary={boundary}"
        )
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()

        try:
            while True:
                frame = _build_frame()
                ok, buffer = cv2.imencode(".jpg", frame)
                if not ok:
                    break
                jpg = buffer.tobytes()
                self.wfile.write(f"--{boundary}\r\n".encode("ascii"))
                self.wfile.write(b"Content-Type: image/jpeg\r\n")
                self.wfile.write(f"Content-Length: {len(jpg)}\r\n\r\n".encode("ascii"))
                self.wfile.write(jpg)
                self.wfile.write(b"\r\n")
                self.wfile.flush()
                time.sleep(1 / 15)
        except (BrokenPipeError, ConnectionResetError):
            pass
        finally:
            with STATE.lock:
                STATE.client_count = max(0, STATE.client_count - 1)

    def log_message(self, fmt, *args):
        return


def ensure_server():
    global _SERVER_STARTED, _SERVER_INSTANCE
    with _SERVER_LOCK:
        if _SERVER_STARTED:
            return
        _SERVER_INSTANCE = _ThreadedHTTPServer((HOST, PORT), _SimulatorRequestHandler)
        thread = threading.Thread(
            target=_SERVER_INSTANCE.serve_forever, name="testcamera-web", daemon=True
        )
        thread.start()
        _SERVER_STARTED = True
        ensure_motion_thread()


class SimulatedViscaSocket:
    def __init__(self, ip, port):
        ensure_server()
        self.ip = ip
        self.port = port
        self._closed = False
        self._pending_reply = "9051ff"
        self._lock = threading.Lock()

    def connect(self, address):
        self.ip, self.port = address

    def send(self, data):
        if self._closed:
            raise OSError("Socket is closed")
        command_hex = data.hex()
        reply = apply_visca_command(command_hex)
        with self._lock:
            self._pending_reply = reply

    def recv(self, _size):
        if self._closed:
            raise OSError("Socket is closed")
        with self._lock:
            reply = self._pending_reply
            self._pending_reply = "9051ff"
        return bytes.fromhex(reply)

    def close(self):
        self._closed = True
