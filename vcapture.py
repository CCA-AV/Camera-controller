import contextlib
from multiprocessing import Process, Value, Queue
import cv2
import time
from warnings import warn


class vcapture(Process):
    def __init__(self, target):
        super().__init__()
        self.target = target
        self._running = Value("b", True)
        self._frame_queue = Queue(maxsize=1)  # Only keep latest frame
        self._current_frame = None
        self.daemon = True

    def run(self):
        cap = cv2.VideoCapture(self.target)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

        if not cap.isOpened():
            warn(f"[vcapture] ERROR: Failed to open video source: {self.target}")
            self.running.value = False
            return

        try:
            failed_reads = 0

            while cap.isOpened() and self._running.value:
                # Set a timeout for reading to make shutdown more responsive
                cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                ret, frame = cap.read()

                if not ret:
                    failed_reads += 1
                    # Check if we should stop before attempting reconnection
                    if not self._running.value:
                        break

                    if failed_reads > 10:
                        warn(
                            "[vcapture] Too many failed reads, attempting to reconnect..."
                        )
                        cap.release()
                        time.sleep(1)
                        # Check again if we should stop
                        if not self._running.value:
                            break
                        cap = cv2.VideoCapture(self.target)
                        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                        failed_reads = 0
                        if not cap.isOpened():
                            warn("[vcapture] ERROR: Failed to reconnect")
                            break
                    else:
                        # Brief sleep to avoid busy waiting and check running flag more often
                        time.sleep(0.01)
                    continue

                failed_reads = 0
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                # Put frame in queue, replacing any existing frame
                with contextlib.suppress(Exception):
                    if self._frame_queue.full():
                        self._frame_queue.get_nowait()  # Remove old frame
                    self._frame_queue.put_nowait(frame)
        finally:
            # Ensure VideoCapture is always released
            cap.release()
            self._running.value = False

    @property
    def current_frame(self):
        """Get the most recent frame"""
        # Get latest frame if available
        with contextlib.suppress(Exception):
            while not self._frame_queue.empty():
                self._current_frame = self._frame_queue.get_nowait()
        return self._current_frame

    @property
    def running(self):
        return self._running.value

    def release(self):
        """Release resources and stop the process"""
        self._running.value = False
        self.join(timeout=1.0)
