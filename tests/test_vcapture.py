#!/usr/bin/env python3
"""
Tests for vcapture.py module.
Tests the multiprocessing video capture functionality.
Heavily mocked to prevent actual processes and cv2 resources from being created.
"""

import unittest
import unittest.mock
from unittest.mock import Mock, patch, MagicMock, PropertyMock
import numpy as np
import cv2

# Import the module under test
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestVcaptureInit(unittest.TestCase):
    """Test vcapture initialization"""

    @patch("vcapture.Queue")
    @patch("vcapture.Value")
    @patch("vcapture.Process.__init__", return_value=None)
    @patch("vcapture.Process.daemon", new_callable=PropertyMock)
    def test_init_with_target(
        self, mock_daemon, mock_process_init, mock_value, mock_queue
    ):
        """Test vcapture initialization with target"""
        # Setup mocks
        mock_running = Mock()
        mock_running.value = True
        mock_value.return_value = mock_running

        mock_frame_queue = Mock()
        mock_frame_queue._maxsize = 1
        mock_queue.return_value = mock_frame_queue

        from vcapture import vcapture

        target = "rtsp://192.168.0.25:554/2"
        cap = vcapture(target)

        self.assertEqual(cap.target, target)
        mock_value.assert_called_once_with("b", True)
        mock_queue.assert_called_once_with(maxsize=1)
        self.assertTrue(cap._running.value)
        self.assertEqual(cap._frame_queue._maxsize, 1)
        self.assertIsNone(cap._current_frame)


class TestVcaptureProperties(unittest.TestCase):
    """Test vcapture properties"""

    def setUp(self):
        with patch("vcapture.Queue") as mock_queue, patch(
            "vcapture.Value"
        ) as mock_value, patch("vcapture.Process.__init__", return_value=None), patch(
            "vcapture.Process.daemon", new_callable=PropertyMock
        ):

            # Setup mocks
            mock_running = Mock()
            mock_running.value = True
            mock_value.return_value = mock_running

            mock_frame_queue = Mock()
            mock_frame_queue.empty.return_value = True
            mock_queue.return_value = mock_frame_queue

            from vcapture import vcapture

            self.cap = vcapture("test_target")

    def test_running_property(self):
        """Test running property getter"""
        self.assertTrue(self.cap.running)

        # Change the value and test again
        self.cap._running.value = False
        self.assertFalse(self.cap.running)

    def test_current_frame_property_empty_queue(self):
        """Test current_frame property with empty queue"""
        # Initially no frame should be available
        self.assertIsNone(self.cap.current_frame)


class TestVcaptureRun(unittest.TestCase):
    """Test vcapture run method (the main capture loop)"""

    def setUp(self):
        with patch("vcapture.Queue") as mock_queue, patch(
            "vcapture.Value"
        ) as mock_value, patch("vcapture.Process.__init__", return_value=None), patch(
            "vcapture.Process.daemon", new_callable=PropertyMock
        ):

            # Setup mocks
            mock_running = Mock()
            mock_running.value = True
            mock_value.return_value = mock_running

            mock_frame_queue = Mock()
            mock_frame_queue.full.return_value = False
            mock_queue.return_value = mock_frame_queue

            from vcapture import vcapture

            self.cap = vcapture("test_target")

    @patch("vcapture.cv2.VideoCapture")
    def test_run_successful_capture(self, mock_video_capture_class):
        """Test successful video capture run"""
        # Setup mock
        mock_cap = Mock()
        mock_video_capture_class.return_value = mock_cap
        mock_cap.isOpened.return_value = True

        # Mock successful frame reads
        mock_frame = np.zeros((480, 640, 3), dtype=np.uint8)

        # Stop the process after a few iterations
        call_count = 0

        def stop_after_calls(*args):
            nonlocal call_count
            call_count += 1
            if call_count >= 3:
                self.cap._running.value = False
            return (True, mock_frame) if call_count <= 2 else (False, None)

        mock_cap.read.side_effect = stop_after_calls

        with patch("vcapture.cv2.cvtColor", return_value=mock_frame):
            # Run the capture
            self.cap.run()

        # Verify VideoCapture was created and configured
        mock_video_capture_class.assert_called_once_with("test_target")
        mock_cap.set.assert_any_call(cv2.CAP_PROP_BUFFERSIZE, 1)
        mock_cap.isOpened.assert_called()
        mock_cap.read.assert_called()
        mock_cap.release.assert_called_once()

    @patch("vcapture.cv2.VideoCapture")
    def test_run_failed_to_open_warning(self, mock_video_capture_class):
        """Test run method issues warning when VideoCapture fails to open"""
        # Setup mock
        mock_cap = Mock()
        mock_video_capture_class.return_value = mock_cap
        mock_cap.isOpened.return_value = False

        # Run the capture
        with patch("vcapture.warn") as mock_warn:
            self.cap.run()

        # Verify warning was issued and running was set to False
        mock_warn.assert_called_once_with(
            "[vcapture] ERROR: Failed to open video source: test_target"
        )
        self.assertFalse(self.cap._running.value)
        # Should return early, so no read attempts
        mock_cap.read.assert_not_called()

    @patch("vcapture.cv2.VideoCapture")
    @patch("vcapture.time.sleep")
    def test_run_failed_reads_reconnection_warning(
        self, mock_sleep, mock_video_capture_class
    ):
        """Test run method handles multiple failed reads and issues reconnection warning"""
        # Setup mock for initial VideoCapture
        mock_cap_initial = Mock()
        mock_cap_reconnect = Mock()
        mock_video_capture_class.side_effect = [mock_cap_initial, mock_cap_reconnect]

        # Both captures should report as opened
        mock_cap_initial.isOpened.return_value = True
        mock_cap_reconnect.isOpened.return_value = True

        # Simulate exactly 11 failed reads to trigger reconnection, then stop
        call_count = 0

        def failed_reads_trigger_reconnection(*args):
            nonlocal call_count
            call_count += 1
            # Stop after reconnection is triggered and new VideoCapture is created
            if call_count > 11 and mock_video_capture_class.call_count > 1:
                self.cap._running.value = False
            return (False, None)  # Always return failed read

        mock_cap_initial.read.side_effect = failed_reads_trigger_reconnection
        mock_cap_reconnect.read.side_effect = failed_reads_trigger_reconnection

        with patch("vcapture.warn") as mock_warn:
            self.cap.run()

        # Verify reconnection warning was issued
        mock_warn.assert_called_with(
            "[vcapture] Too many failed reads, attempting to reconnect..."
        )
        # Verify both types of sleep were called: brief sleeps (0.01) and reconnection sleep (1)
        mock_sleep.assert_any_call(1)  # Reconnection sleep
        mock_sleep.assert_any_call(0.01)  # Brief sleeps for failed reads
        # Verify cap was released and recreated
        mock_cap_initial.release.assert_called()
        # VideoCapture should be called twice: initial + reconnection
        self.assertEqual(mock_video_capture_class.call_count, 2)

    @patch("vcapture.cv2.VideoCapture")
    @patch("vcapture.time.sleep")
    def test_run_failed_reconnection_warning(
        self, mock_sleep, mock_video_capture_class
    ):
        """Test run method warns when reconnection fails"""
        # Setup mocks for initial success then failed reconnection
        mock_cap_initial = Mock()
        mock_cap_initial.isOpened.return_value = True

        mock_cap_reconnect = Mock()
        mock_cap_reconnect.isOpened.return_value = False  # Reconnection fails

        mock_video_capture_class.side_effect = [mock_cap_initial, mock_cap_reconnect]

        # Simulate 11 failed reads to trigger reconnection
        call_count = 0

        def trigger_reconnection(*args):
            nonlocal call_count
            call_count += 1
            return (False, None)  # Always return failed read

        mock_cap_initial.read.side_effect = trigger_reconnection

        with patch("vcapture.warn") as mock_warn:
            self.cap.run()

        # Verify both warnings were issued
        expected_calls = [
            unittest.mock.call(
                "[vcapture] Too many failed reads, attempting to reconnect..."
            ),
            unittest.mock.call("[vcapture] ERROR: Failed to reconnect"),
        ]
        mock_warn.assert_has_calls(expected_calls)
        # Verify reconnection was attempted
        self.assertEqual(mock_video_capture_class.call_count, 2)
        mock_cap_initial.release.assert_called()

    @patch("vcapture.cv2.VideoCapture")
    @patch("vcapture.time.sleep")
    def test_run_brief_sleep_on_failed_reads(
        self, mock_sleep, mock_video_capture_class
    ):
        """Test run method does brief sleep for failed reads <= 10"""
        # Setup mock
        mock_cap = Mock()
        mock_video_capture_class.return_value = mock_cap
        mock_cap.isOpened.return_value = True

        # Simulate 5 failed reads then stop
        call_count = 0

        def few_failed_reads(*args):
            nonlocal call_count
            call_count += 1
            if call_count > 5:
                self.cap._running.value = False
            return (False, None)  # Always return failed read

        mock_cap.read.side_effect = few_failed_reads

        with patch("vcapture.warn") as mock_warn:
            self.cap.run()

        # Should not trigger reconnection warning
        mock_warn.assert_not_called()
        # Should call brief sleep (0.01) multiple times, not reconnection sleep (1)
        mock_sleep.assert_called_with(0.01)
        # Should not trigger reconnection
        self.assertEqual(mock_video_capture_class.call_count, 1)
        mock_cap.release.assert_called_once()  # Only final cleanup

    @patch("vcapture.cv2.VideoCapture")
    def test_run_stops_on_running_flag_during_failed_reads(
        self, mock_video_capture_class
    ):
        """Test run method respects _running flag during failed read handling"""
        # Setup mock
        mock_cap = Mock()
        mock_video_capture_class.return_value = mock_cap
        mock_cap.isOpened.return_value = True

        # Simulate failed reads, but set running to False after a few
        call_count = 0

        def failed_reads_with_stop(*args):
            nonlocal call_count
            call_count += 1
            if call_count == 3:  # Stop running after 3 failed reads
                self.cap._running.value = False
            return (False, None)  # Always return failed read

        mock_cap.read.side_effect = failed_reads_with_stop

        self.cap.run()

        # Should exit cleanly without triggering reconnection
        self.assertEqual(mock_video_capture_class.call_count, 1)
        mock_cap.release.assert_called_once()


class TestVcaptureRelease(unittest.TestCase):
    """Test vcapture release method"""

    def setUp(self):
        with patch("vcapture.Queue") as mock_queue, patch(
            "vcapture.Value"
        ) as mock_value, patch("vcapture.Process.__init__", return_value=None), patch(
            "vcapture.Process.daemon", new_callable=PropertyMock
        ):

            # Setup mocks
            mock_running = Mock()
            mock_running.value = True
            mock_value.return_value = mock_running

            mock_frame_queue = Mock()
            mock_queue.return_value = mock_frame_queue

            from vcapture import vcapture

            self.cap = vcapture("test_target")

    @patch("vcapture.Process.join")
    def test_release(self, mock_join):
        """Test release method stops the process"""
        self.cap.release()

        # Verify running was set to False and join was called
        self.assertFalse(self.cap._running.value)
        mock_join.assert_called_once_with(timeout=1.0)


if __name__ == "__main__":
    unittest.main()
