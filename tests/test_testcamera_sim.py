import json
import os
import sys
import time
from urllib.request import urlopen

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from controller import Camera
from camera_streams import TESTCAMERA_DEFAULT_STREAM_URL, stream_url_for_camera
from cameras import testcamera_sim as sim


def _reset_sim_state():
    with sim.STATE.lock:
        sim.STATE.power = 1
        sim.STATE.focus_mode = 2
        sim.STATE.backlight = 3
        sim.STATE.zoom_pos = 0
        sim.STATE.focus_pos = 0
        sim.STATE.pan_pos = 0x8000
        sim.STATE.tilt_pos = 0x8000
        sim.STATE.brightness = 128
        sim.STATE.contrast = 128
        sim.STATE.last_command = ""
        sim.STATE.command_count = 0
        sim.STATE.inquiry_count = 0
        sim.STATE.pan_velocity = 0.0
        sim.STATE.tilt_velocity = 0.0
        sim.STATE.zoom_velocity = 0.0
        sim.STATE.focus_velocity = 0.0
        sim.STATE.presets = {}


@pytest.fixture(autouse=True)
def reset_simulator():
    _reset_sim_state()
    yield
    _reset_sim_state()


def test_stream_url_for_camera_routing():
    assert (
        stream_url_for_camera({"ip": "10.0.0.1", "type": "ptzoptics"})
        == "rtsp://10.0.0.1:554/2"
    )
    assert (
        stream_url_for_camera({"ip": "10.0.0.1", "type": "testcamera"})
        == TESTCAMERA_DEFAULT_STREAM_URL
    )
    assert (
        stream_url_for_camera(
            {
                "ip": "10.0.0.1",
                "type": "testcamera",
                "stream_url": "http://127.0.0.1:9999/custom.mjpg",
            }
        )
        == "http://127.0.0.1:9999/custom.mjpg"
    )


def test_testcamera_state_updates_from_visca_commands():
    cam = Camera(ip="127.0.0.1", camera_type="testcamera")
    try:
        cam.zoom("direct", 1000)
        cam.focus("direct", 777)
        cam.move("abs", pan=0x1234, tilt=0x5678, pan_speed=10, tilt_speed=11)
        cam.focus_mode("manual")
        cam.backlight = True

        snapshot = sim.STATE.snapshot()
        assert snapshot["zoom_pos"] == 1000
        assert snapshot["focus_pos"] == 777
        assert snapshot["pan_pos"] == 0x1234
        assert snapshot["tilt_pos"] == 0x5678
        assert snapshot["focus_mode"] == 3
        assert snapshot["backlight"] == 2
    finally:
        cam.close()


def test_testcamera_incremental_commands_update_state():
    cam = Camera(ip="127.0.0.1", camera_type="testcamera")
    try:
        before = sim.STATE.snapshot()
        cam.zoom("tele")
        cam.focus("far")
        cam.pan_left(7, 7)
        time.sleep(0.2)
        after = sim.STATE.snapshot()

        assert after["zoom_pos"] > before["zoom_pos"]
        assert after["focus_pos"] > before["focus_pos"]
        assert after["pan_pos"] < before["pan_pos"]
    finally:
        cam.close()


def test_pan_continues_until_pan_stop():
    cam = Camera(ip="127.0.0.1", camera_type="testcamera")
    try:
        cam.pan_left(7, 7)
        time.sleep(0.2)
        first = sim.STATE.snapshot()["pan_pos"]
        time.sleep(0.2)
        second = sim.STATE.snapshot()["pan_pos"]
        assert second < first

        cam.pan_stop()
        stopped = sim.STATE.snapshot()["pan_pos"]
        time.sleep(0.2)
        stopped_after = sim.STATE.snapshot()["pan_pos"]
        assert stopped_after == stopped
    finally:
        cam.close()


def test_zoom_and_focus_continue_until_stop():
    cam = Camera(ip="127.0.0.1", camera_type="testcamera")
    try:
        cam.zoom("tele")
        cam.focus("far")
        time.sleep(0.2)
        first = sim.STATE.snapshot()
        time.sleep(0.2)
        second = sim.STATE.snapshot()
        assert second["zoom_pos"] > first["zoom_pos"]
        assert second["focus_pos"] > first["focus_pos"]

        cam.zoom_stop()
        cam.focus_stop()
        stopped = sim.STATE.snapshot()
        time.sleep(0.2)
        stopped_after = sim.STATE.snapshot()
        assert stopped_after["zoom_pos"] == stopped["zoom_pos"]
        assert stopped_after["focus_pos"] == stopped["focus_pos"]
    finally:
        cam.close()


def test_testcamera_web_stats_endpoint():
    cam = Camera(ip="127.0.0.1", camera_type="testcamera")
    try:
        with urlopen(f"http://{sim.HOST}:{sim.PORT}{sim.STATS_PATH}", timeout=2) as response:
            payload = json.loads(response.read().decode("utf-8"))
        assert "zoom_pos" in payload
        assert "focus_pos" in payload
        assert "command_count" in payload
    finally:
        cam.close()
