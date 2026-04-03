TESTCAMERA_DEFAULT_STREAM_URL = "http://127.0.0.1:8765/stream.mjpg"


def stream_url_for_camera(cam_cfg):
    """
    Resolve stream URL with backward-compatible defaults.
    """
    stream_url = cam_cfg.get("stream_url")
    if isinstance(stream_url, str) and stream_url.strip():
        return stream_url.strip()

    cam_type = str(cam_cfg.get("type", "ptzoptics")).strip().lower()
    if cam_type == "testcamera":
        return TESTCAMERA_DEFAULT_STREAM_URL

    ip = str(cam_cfg.get("ip", "")).strip()
    return f"rtsp://{ip}:554/2"
