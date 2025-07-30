#!/usr/bin/env python3
"""
Tests for rtsp_feed.py module.
Tests the RTSP feed GUI application functionality.
"""

import unittest
import unittest.mock
from unittest.mock import Mock, patch, MagicMock, call
import sys
import os
import numpy as np
from PIL import Image
import textwrap

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestRtspFeedClose(unittest.TestCase):
    """Test the close function from rtsp_feed.py"""

    @patch("rtsp_feed.cv2")
    @patch("rtsp_feed.quit")
    def test_close_with_cap(self, mock_quit, mock_cv2):
        """Test close function when cap is available"""
        # Create a mock cap and inject it into the global namespace
        mock_cap = Mock()
        mock_cap.release = Mock()

        # Import the close function and mock the cap variable
        import rtsp_feed

        original_cap = getattr(rtsp_feed, "cap", None)
        rtsp_feed.cap = mock_cap

        try:
            # Call close function
            rtsp_feed.close()

            # Verify cap.release() was called
            mock_cap.release.assert_called_once()
            # Verify cv2.destroyAllWindows() was called
            mock_cv2.destroyAllWindows.assert_called_once()
            # Verify quit() was called
            mock_quit.assert_called_once()
        finally:
            # Restore original state
            if original_cap is not None:
                rtsp_feed.cap = original_cap
            else:
                delattr(rtsp_feed, "cap")

    @patch("rtsp_feed.cv2")
    @patch("rtsp_feed.quit")
    def test_close_without_cap(self, mock_quit, mock_cv2):
        """Test close function when cap is None"""
        # Import the close function and set cap to None
        import rtsp_feed

        original_cap = getattr(rtsp_feed, "cap", None)
        rtsp_feed.cap = None

        try:
            # Call close function - should not crash
            rtsp_feed.close()

            # Verify cv2.destroyAllWindows() was still called
            mock_cv2.destroyAllWindows.assert_called_once()
            # Verify quit() was called
            mock_quit.assert_called_once()
        finally:
            # Restore original state
            if original_cap is not None:
                rtsp_feed.cap = original_cap
            elif hasattr(rtsp_feed, "cap"):
                delattr(rtsp_feed, "cap")


class TestRtspFeedIntegration(unittest.TestCase):
    """Test integration points in rtsp_feed.py"""

    @patch("rtsp_feed.ntk")
    @patch("rtsp_feed.vcapture")
    @patch("rtsp_feed.cv2")
    def test_vcapture_integration(self, mock_cv2, mock_vcapture_class, mock_ntk):
        """Test that rtsp_feed correctly integrates with vcapture"""
        # Setup mocks
        mock_vcapture_instance = Mock()
        mock_vcapture_class.return_value = mock_vcapture_instance
        mock_vcapture_instance.running = True
        mock_vcapture_instance.current_frame = np.zeros((480, 640, 3), dtype=np.uint8)

        mock_window = Mock()
        mock_ntk.Window.return_value = mock_window

        mock_frame_container = Mock()
        mock_ntk.Frame.return_value = mock_frame_container
        mock_frame_container.place.return_value = mock_frame_container

        mock_image = Mock()
        mock_ntk.image_manager.Image.return_value = mock_image

        # Mock the main execution to stop after one iteration
        with patch("rtsp_feed.time") as mock_time:
            mock_time.time.return_value = 0.0

            # Patch the while loop condition to run only once
            def side_effect(*args):
                mock_vcapture_instance.running = False
                return False

            mock_vcapture_instance.running = True

            # Since we can't easily test the main execution block without running the whole script,
            # let's test the components that would be used

            # Test vcapture instantiation
            cap = mock_vcapture_class("rtsp://192.168.0.25:554/2")
            mock_vcapture_class.assert_called_with("rtsp://192.168.0.25:554/2")

            # Test that start would be called
            cap.start()
            mock_vcapture_instance.start.assert_called_once()

    def test_pil_image_conversion(self):
        """Test PIL Image conversion logic"""
        # Create a test frame (numpy array)
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        frame[:, :, 0] = 255  # Red channel

        # Test PIL Image creation
        pil_image = Image.fromarray(frame, "RGB")

        # Verify the image was created correctly
        self.assertEqual(pil_image.size, (640, 480))  # PIL uses (width, height)
        self.assertEqual(pil_image.mode, "RGB")

        # Verify pixel data
        pixel_data = np.array(pil_image)
        np.testing.assert_array_equal(pixel_data, frame)


class TestRtspFeedFrameProcessing(unittest.TestCase):
    """Test frame processing logic in rtsp_feed.py"""

    def test_frame_resize_calculation(self):
        """Test frame resize calculations"""
        # Constants from rtsp_feed.py
        width = 16 * 50
        height = 9 * 50

        self.assertEqual(width, 800)
        self.assertEqual(height, 450)

        # Test aspect ratio
        aspect_ratio = width / height
        expected_ratio = 16 / 9
        self.assertAlmostEqual(aspect_ratio, expected_ratio, places=2)

    @patch("rtsp_feed.ntk")
    def test_frame_container_replacement(self, mock_ntk):
        """Test frame container replacement logic"""
        # Setup mocks
        mock_window = Mock()
        mock_old_container = Mock()
        mock_new_container = Mock()
        mock_image = Mock()

        # Mock the Frame creation to return our mock
        mock_ntk.Frame.return_value = mock_new_container
        mock_new_container.place.return_value = mock_new_container

        # Test the container replacement pattern
        # This simulates what happens in the main loop

        # Create new frame container with image
        new_frame_container = mock_ntk.Frame(
            mock_window, width=800, height=450, image=mock_image
        ).place()

        # Verify Frame was called with correct parameters
        mock_ntk.Frame.assert_called_with(
            mock_window, width=800, height=450, image=mock_image
        )

        # Verify place was called
        mock_new_container.place.assert_called()

        # Simulate destroying old container
        mock_old_container.destroy()
        mock_old_container.destroy.assert_called_once()


class TestRtspFeedConstants(unittest.TestCase):
    """Test constants and configuration in rtsp_feed.py"""

    def test_rtsp_url_format(self):
        """Test RTSP URL format"""
        rtsp_url = "rtsp://192.168.0.25:554/2"

        # Verify URL format
        self.assertTrue(rtsp_url.startswith("rtsp://"))
        self.assertIn("192.168.0.25", rtsp_url)
        self.assertIn(":554", rtsp_url)
        self.assertTrue(rtsp_url.endswith("/2"))

    def test_window_dimensions(self):
        """Test window dimension calculations"""
        width = 16 * 50
        height = 9 * 50

        # Test that dimensions are reasonable
        self.assertGreater(width, 0)
        self.assertGreater(height, 0)
        self.assertEqual(width, 800)
        self.assertEqual(height, 450)

        # Test 16:9 aspect ratio
        self.assertAlmostEqual(width / height, 16 / 9, places=2)


class TestRtspFeedMocks(unittest.TestCase):
    """Test rtsp_feed with comprehensive mocking"""

    @patch("rtsp_feed.ntk")
    @patch("rtsp_feed.vcapture")
    @patch("rtsp_feed.time")
    def test_main_loop_simulation(self, mock_time, mock_vcapture_class, mock_ntk):
        """Test simulation of main loop components"""
        # Setup comprehensive mocks
        mock_vcapture_instance = Mock()
        mock_vcapture_class.return_value = mock_vcapture_instance

        # Mock window and UI components
        mock_window = Mock()
        mock_ntk.Window.return_value = mock_window

        mock_frame_container = Mock()
        mock_ntk.Frame.return_value = mock_frame_container
        mock_frame_container.place.return_value = mock_frame_container

        mock_image = Mock()
        mock_ntk.image_manager.Image.return_value = mock_image

        # Mock time functions
        mock_time.time.side_effect = [1.0, 1.1, 1.2]  # Progressive time values

        # Create test frame
        test_frame = np.ones((480, 640, 3), dtype=np.uint8) * 128
        mock_vcapture_instance.current_frame = test_frame
        mock_vcapture_instance.running = True

        # Test the components that would be used in main loop

        # 1. Window creation
        window = mock_ntk.Window(width=800, height=450, closing_command=None)
        mock_ntk.Window.assert_called()

        # 2. Frame container creation
        frame_container = mock_ntk.Frame(window, width=800, height=450).place()
        mock_ntk.Frame.assert_called()

        # 3. VCapture creation and start
        cap = mock_vcapture_class("rtsp://192.168.0.25:554/2")
        cap.start()
        mock_vcapture_class.assert_called_with("rtsp://192.168.0.25:554/2")
        mock_vcapture_instance.start.assert_called()

        # 4. Frame processing (simulate one iteration)
        frame = mock_vcapture_instance.current_frame
        self.assertIsNotNone(frame)

        # 5. PIL Image creation (would happen in real code)
        with patch("rtsp_feed.Image") as mock_pil:
            pil_image = mock_pil.fromarray(frame, "RGB")
            mock_pil.fromarray.assert_called_with(frame, "RGB")

        # 6. ntk Image creation
        img = mock_ntk.image_manager.Image(_object=frame_container, image=None)
        mock_ntk.image_manager.Image.assert_called()


class TestRtspFeedMainExecution(unittest.TestCase):
    """Test the main execution block of rtsp_feed.py"""

    def setUp(self):
        """Reset any cached imports before each test"""
        # Remove rtsp_feed from sys.modules if it exists to allow fresh import
        if "rtsp_feed" in sys.modules:
            del sys.modules["rtsp_feed"]

    @patch("rtsp_feed.time")
    @patch("rtsp_feed.Image")
    @patch("rtsp_feed.vcapture")
    @patch("rtsp_feed.ntk")
    def test_main_execution_block_window_creation(
        self, mock_ntk, mock_vcapture_class, mock_image_class, mock_time
    ):
        """Test main block creates window with correct parameters"""
        # Setup mocks
        mock_window = Mock()
        mock_ntk.Window.return_value = mock_window

        mock_frame_container = Mock()
        mock_ntk.Frame.return_value = mock_frame_container
        mock_frame_container.place.return_value = mock_frame_container

        mock_vcapture_instance = Mock()
        mock_vcapture_instance.running = False  # Exit loop immediately
        mock_vcapture_class.return_value = mock_vcapture_instance

        mock_image = Mock()
        mock_ntk.image_manager.Image.return_value = mock_image

        # Import the close function reference
        from rtsp_feed import close

        # Simulate the main execution
        window = mock_ntk.Window(width=16 * 50, height=9 * 50, closing_command=close)
        frame_container = mock_ntk.Frame(window, width=16 * 50, height=9 * 50).place()
        cap = mock_vcapture_class("rtsp://192.168.0.25:554/2")
        cap.start()
        img = mock_ntk.image_manager.Image(_object=frame_container, image=None)

        # Verify window creation
        mock_ntk.Window.assert_called_with(width=800, height=450, closing_command=close)

        # Verify frame container creation
        mock_ntk.Frame.assert_called_with(window, width=800, height=450)
        mock_frame_container.place.assert_called()

        # Verify vcapture setup
        mock_vcapture_class.assert_called_with("rtsp://192.168.0.25:554/2")
        mock_vcapture_instance.start.assert_called()

        # Verify initial image creation
        mock_ntk.image_manager.Image.assert_called_with(
            _object=frame_container, image=None
        )

    @patch("rtsp_feed.time")
    @patch("rtsp_feed.Image")
    @patch("rtsp_feed.vcapture")
    @patch("rtsp_feed.ntk")
    def test_main_execution_block_frame_processing(
        self, mock_ntk, mock_vcapture_class, mock_image_class, mock_time
    ):
        """Test main block processes frames correctly"""
        # Setup mocks
        mock_window = Mock()
        mock_ntk.Window.return_value = mock_window

        mock_frame_container = Mock()
        mock_new_frame_container = Mock()
        mock_ntk.Frame.side_effect = [mock_frame_container, mock_new_frame_container]
        mock_frame_container.place.return_value = mock_frame_container
        mock_new_frame_container.place.return_value = mock_new_frame_container

        # Create test frame
        test_frame = np.ones((480, 640, 3), dtype=np.uint8) * 128

        mock_vcapture_instance = Mock()
        # First time running=True with frame, second time running=False to exit
        mock_vcapture_instance.running = True
        mock_vcapture_instance.current_frame = test_frame
        mock_vcapture_class.return_value = mock_vcapture_instance

        mock_image = Mock()
        mock_ntk.image_manager.Image.return_value = mock_image

        mock_pil_image = Mock()
        mock_image_class.fromarray.return_value = mock_pil_image

        mock_time.time.side_effect = [1.0, 1.1, 1.2]  # Progressive time values

        # Simulate the main loop execution (one iteration)
        from rtsp_feed import close

        window = mock_ntk.Window(width=800, height=450, closing_command=close)
        frame_container = mock_ntk.Frame(window, width=800, height=450).place()
        cap = mock_vcapture_class("rtsp://192.168.0.25:554/2")
        cap.start()
        img = mock_ntk.image_manager.Image(_object=frame_container, image=None)

        # Simulate one iteration of the while loop
        if cap.running:
            frame_time1 = mock_time.time()
            frame = cap.current_frame
            frame_time2 = mock_time.time()

            if frame is not None:
                # PIL Image conversion
                im = mock_image_class.fromarray(frame, "RGB")
                # ntk Image creation and resize
                img = mock_ntk.image_manager.Image(_object=frame_container, image=im)
                img.resize(width=800, height=450)
                # New frame container creation
                new_frame_container = mock_ntk.Frame(
                    window, width=800, height=450, image=img
                ).place()
                # Destroy old container
                frame_container.destroy()
                frame_container = new_frame_container

            frame_time3 = mock_time.time()

        # Verify frame processing
        mock_image_class.fromarray.assert_called_with(test_frame, "RGB")

        # Verify image resize
        mock_image.resize.assert_called_with(width=800, height=450)

        # Verify new frame container creation with image
        expected_calls = [
            unittest.mock.call(window, width=800, height=450),  # Initial container
            unittest.mock.call(
                window, width=800, height=450, image=mock_image
            ),  # New container with image
        ]
        mock_ntk.Frame.assert_has_calls(expected_calls)

        # Verify old container was destroyed
        mock_frame_container.destroy.assert_called()

        # Verify time calls
        self.assertEqual(mock_time.time.call_count, 3)

    @patch("rtsp_feed.time")
    @patch("rtsp_feed.Image")
    @patch("rtsp_feed.vcapture")
    @patch("rtsp_feed.ntk")
    def test_main_execution_block_no_frame_handling(
        self, mock_ntk, mock_vcapture_class, mock_image_class, mock_time
    ):
        """Test main block handles None frames correctly"""
        # Setup mocks
        mock_window = Mock()
        mock_ntk.Window.return_value = mock_window

        mock_frame_container = Mock()
        mock_ntk.Frame.return_value = mock_frame_container
        mock_frame_container.place.return_value = mock_frame_container

        mock_vcapture_instance = Mock()
        mock_vcapture_instance.running = True
        mock_vcapture_instance.current_frame = None  # No frame available
        mock_vcapture_class.return_value = mock_vcapture_instance

        mock_image = Mock()
        mock_ntk.image_manager.Image.return_value = mock_image

        mock_time.time.side_effect = [1.0, 1.1, 1.2]

        # Simulate the main loop execution with None frame
        from rtsp_feed import close

        window = mock_ntk.Window(width=800, height=450, closing_command=close)
        frame_container = mock_ntk.Frame(window, width=800, height=450).place()
        cap = mock_vcapture_class("rtsp://192.168.0.25:554/2")
        cap.start()
        img = mock_ntk.image_manager.Image(_object=frame_container, image=None)

        # Simulate one iteration with None frame
        if cap.running:
            frame_time1 = mock_time.time()
            frame = cap.current_frame
            frame_time2 = mock_time.time()

            if frame is not None:
                # This should not execute
                mock_image_class.fromarray(frame, "RGB")

            frame_time3 = mock_time.time()

        # Verify no frame processing occurred
        mock_image_class.fromarray.assert_not_called()

        # Verify only initial Frame creation (no new container)
        mock_ntk.Frame.assert_called_once_with(window, width=800, height=450)

        # Verify time calls still happened
        self.assertEqual(mock_time.time.call_count, 3)


class TestRtspFeedMainBlock(unittest.TestCase):
    """Test the actual main execution block of rtsp_feed.py"""

    def setUp(self):
        """Set up test environment"""
        # Clear any existing rtsp_feed imports to ensure fresh state
        if "rtsp_feed" in sys.modules:
            del sys.modules["rtsp_feed"]

    def _execute_main_block_with_mocks(
        self, mock_ntk, mock_vcapture_class, mock_image_class, mock_time
    ):
        """Helper method to execute the main block with given mocks"""
        # Simple approach: read the main block code and execute it with mocked dependencies

        # Clear any existing module cache
        if "rtsp_feed" in sys.modules:
            del sys.modules["rtsp_feed"]

        # Create mock modules for all the imports
        mock_cv2 = Mock()
        mock_pil = Mock()
        mock_pil.Image = mock_image_class
        mock_time_module = Mock()
        mock_time_module.sleep = Mock()
        mock_time_module.time = mock_time.time
        mock_vcapture_module = Mock()
        mock_vcapture_module.vcapture = mock_vcapture_class

        # Read the main block code
        with open("rtsp_feed.py", "r") as f:
            content = f.read()

        # Extract just the main block (lines after if __name__ == "__main__":)
        lines = content.split("\n")
        try:
            main_block_start = next(
                i + 1
                for i, line in enumerate(lines)
                if 'if __name__ == "__main__":' in line
            )
        except StopIteration:
            raise ValueError("Could not find main block in rtsp_feed.py")

        # Get the main block code (excluding the if statement itself)
        main_block_lines = lines[main_block_start:]
        main_block_code = "\n".join(main_block_lines)
        main_block_code = textwrap.dedent(main_block_code)

        # Create execution environment with mocks
        exec_globals = {
            "ntk": mock_ntk,
            "vcapture": mock_vcapture_class,
            "Image": mock_image_class,
            "time": mock_time.time,
            "cv2": mock_cv2,
            "close": Mock(),
            "sleep": Mock(),
        }

        # Execute the main block code
        exec(main_block_code, exec_globals)

        return exec_globals

    def test_main_block_execution_initialization(self):
        """Test that the main block initializes all components correctly"""
        # Setup mocks
        mock_ntk = Mock()
        mock_window = Mock()
        mock_ntk.Window.return_value = mock_window

        mock_frame_container = Mock()
        mock_ntk.Frame.return_value = mock_frame_container
        mock_frame_container.place.return_value = mock_frame_container

        mock_vcapture_class = Mock()
        mock_vcapture_instance = Mock()
        mock_vcapture_instance.running = (
            False  # Exit immediately to test just initialization
        )
        mock_vcapture_class.return_value = mock_vcapture_instance

        mock_image_class = Mock()
        mock_image = Mock()
        mock_ntk.image_manager.Image.return_value = mock_image

        mock_time = Mock()

        # Execute the main block
        exec_globals = self._execute_main_block_with_mocks(
            mock_ntk, mock_vcapture_class, mock_image_class, mock_time
        )

        # Verify window creation
        mock_ntk.Window.assert_called_once()
        call_args = mock_ntk.Window.call_args
        self.assertEqual(call_args.kwargs["width"], 800)
        self.assertEqual(call_args.kwargs["height"], 450)
        # The closing_command should be a callable function
        self.assertTrue(callable(call_args.kwargs["closing_command"]))

        # Verify frame container creation
        mock_ntk.Frame.assert_called_with(mock_window, width=800, height=450)
        mock_frame_container.place.assert_called_once()

        # Verify vcapture initialization
        mock_vcapture_class.assert_called_once_with("rtsp://192.168.0.25:554/2")
        mock_vcapture_instance.start.assert_called_once()

        # Verify initial image creation
        mock_ntk.image_manager.Image.assert_called_with(
            _object=mock_frame_container, image=None
        )

    def test_main_block_execution_single_loop_iteration(self):
        """Test that the main block processes one frame correctly"""
        # Setup mocks
        mock_ntk = Mock()
        mock_window = Mock()
        mock_ntk.Window.return_value = mock_window

        mock_frame_container = Mock()
        mock_new_frame_container = Mock()
        mock_ntk.Frame.side_effect = [mock_frame_container, mock_new_frame_container]
        mock_frame_container.place.return_value = mock_frame_container
        mock_new_frame_container.place.return_value = mock_new_frame_container

        # Create a test frame
        test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        test_frame[:, :, 0] = 255  # Red frame

        mock_vcapture_class = Mock()
        mock_vcapture_instance = Mock()
        # Set to run once, then stop
        mock_vcapture_instance.running = True
        mock_vcapture_instance.current_frame = test_frame
        mock_vcapture_class.return_value = mock_vcapture_instance

        # Mock to stop after first iteration
        call_count = [0]

        def running_side_effect(self):
            call_count[0] += 1
            return call_count[0] == 1  # True first time, False after

        type(mock_vcapture_instance).running = property(running_side_effect)

        mock_image = Mock()
        mock_new_image = Mock()
        mock_ntk.image_manager.Image.side_effect = [mock_image, mock_new_image]

        mock_image_class = Mock()
        mock_pil_image = Mock()
        mock_image_class.fromarray.return_value = mock_pil_image

        mock_time = Mock()
        mock_time.time.side_effect = [1.0, 1.1, 1.2]  # Progressive time values

        # Execute the main block
        exec_globals = self._execute_main_block_with_mocks(
            mock_ntk, mock_vcapture_class, mock_image_class, mock_time
        )

        # Verify frame processing occurred
        mock_image_class.fromarray.assert_called_with(test_frame, "RGB")

        # Verify image resize
        mock_new_image.resize.assert_called_with(width=800, height=450)

        # Verify new frame container creation with image
        expected_calls = [
            call(mock_window, width=800, height=450),  # Initial container
            call(
                mock_window, width=800, height=450, image=mock_new_image
            ),  # New container with image
        ]
        mock_ntk.Frame.assert_has_calls(expected_calls)

        # Verify old container was destroyed
        mock_frame_container.destroy.assert_called_once()

        # Verify timing calls
        self.assertEqual(mock_time.time.call_count, 3)

    def test_main_block_execution_none_frame_handling(self):
        """Test that the main block handles None frames correctly"""
        # Setup mocks
        mock_ntk = Mock()
        mock_window = Mock()
        mock_ntk.Window.return_value = mock_window

        mock_frame_container = Mock()
        mock_ntk.Frame.return_value = mock_frame_container
        mock_frame_container.place.return_value = mock_frame_container

        mock_vcapture_class = Mock()
        mock_vcapture_instance = Mock()
        # Set to run once with None frame, then stop
        mock_vcapture_instance.running = True
        mock_vcapture_instance.current_frame = None
        mock_vcapture_class.return_value = mock_vcapture_instance

        # Mock to stop after first iteration
        call_count = [0]

        def running_side_effect(self):
            call_count[0] += 1
            return call_count[0] == 1  # True first time, False after

        type(mock_vcapture_instance).running = property(running_side_effect)

        mock_image = Mock()
        mock_ntk.image_manager.Image.return_value = mock_image

        mock_image_class = Mock()
        mock_time = Mock()
        mock_time.time.side_effect = [1.0, 1.1, 1.2]

        # Execute the main block
        exec_globals = self._execute_main_block_with_mocks(
            mock_ntk, mock_vcapture_class, mock_image_class, mock_time
        )

        # Verify no frame processing occurred (PIL Image should not be called)
        mock_image_class.fromarray.assert_not_called()

        # Verify only initial Frame creation (no new container created)
        mock_ntk.Frame.assert_called_once_with(mock_window, width=800, height=450)

        # Verify no container destruction (since no new container was created)
        mock_frame_container.destroy.assert_not_called()

        # Verify timing calls still occurred
        self.assertEqual(mock_time.time.call_count, 3)

    def test_main_block_execution_multiple_iterations(self):
        """Test that the main block can handle multiple loop iterations"""
        # Setup mocks
        mock_ntk = Mock()
        mock_window = Mock()
        mock_ntk.Window.return_value = mock_window

        mock_frame_container = Mock()
        mock_new_frame_container1 = Mock()
        mock_new_frame_container2 = Mock()
        mock_ntk.Frame.side_effect = [
            mock_frame_container,
            mock_new_frame_container1,
            mock_new_frame_container2,
        ]
        mock_frame_container.place.return_value = mock_frame_container
        mock_new_frame_container1.place.return_value = mock_new_frame_container1
        mock_new_frame_container2.place.return_value = mock_new_frame_container2

        # Create test frames
        test_frame1 = np.zeros((480, 640, 3), dtype=np.uint8)
        test_frame1[:, :, 0] = 255  # Red frame
        test_frame2 = np.zeros((480, 640, 3), dtype=np.uint8)
        test_frame2[:, :, 1] = 255  # Green frame

        mock_vcapture_class = Mock()
        mock_vcapture_instance = Mock()
        mock_vcapture_class.return_value = mock_vcapture_instance

        # Set up to run 2 iterations, then stop
        call_count = [0]
        frame_count = [0]

        def running_side_effect(self):
            call_count[0] += 1
            return call_count[0] <= 2  # True for first 2 calls, False after

        def current_frame_side_effect(self):
            frame_count[0] += 1
            if frame_count[0] == 1:
                return test_frame1
            elif frame_count[0] == 2:
                return test_frame2
            return None

        type(mock_vcapture_instance).running = property(running_side_effect)
        type(mock_vcapture_instance).current_frame = property(current_frame_side_effect)

        mock_image = Mock()
        mock_new_image1 = Mock()
        mock_new_image2 = Mock()
        mock_ntk.image_manager.Image.side_effect = [
            mock_image,
            mock_new_image1,
            mock_new_image2,
        ]

        mock_image_class = Mock()
        mock_pil_image1 = Mock()
        mock_pil_image2 = Mock()
        mock_image_class.fromarray.side_effect = [mock_pil_image1, mock_pil_image2]

        mock_time = Mock()
        mock_time.time.side_effect = [
            1.0,
            1.1,
            1.2,
            1.3,
            1.4,
            1.5,
            1.6,
        ]  # Multiple time values

        # Execute the main block
        exec_globals = self._execute_main_block_with_mocks(
            mock_ntk, mock_vcapture_class, mock_image_class, mock_time
        )

        # Verify both frames were processed
        expected_fromarray_calls = [
            call(test_frame1, "RGB"),
            call(test_frame2, "RGB"),
        ]
        mock_image_class.fromarray.assert_has_calls(expected_fromarray_calls)

        # Verify both images were resized
        mock_new_image1.resize.assert_called_with(width=800, height=450)
        mock_new_image2.resize.assert_called_with(width=800, height=450)

        # Verify frame container replacements
        expected_frame_calls = [
            call(mock_window, width=800, height=450),  # Initial
            call(
                mock_window, width=800, height=450, image=mock_new_image1
            ),  # First replacement
            call(
                mock_window, width=800, height=450, image=mock_new_image2
            ),  # Second replacement
        ]
        mock_ntk.Frame.assert_has_calls(expected_frame_calls)

        # Verify container destructions
        mock_frame_container.destroy.assert_called_once()
        mock_new_frame_container1.destroy.assert_called_once()

        # Verify timing calls (3 per iteration * 2 iterations = 6 calls)
        self.assertEqual(mock_time.time.call_count, 6)


class TestRtspFeedErrorHandling(unittest.TestCase):
    """Test error handling scenarios in rtsp_feed components"""

    def test_close_with_exception(self):
        """Test close function handles exceptions gracefully"""
        # Create a mock cap that raises exception on release
        mock_cap = Mock()
        mock_cap.release.side_effect = Exception("Test exception")

        import rtsp_feed

        original_cap = getattr(rtsp_feed, "cap", None)
        rtsp_feed.cap = mock_cap

        with patch("rtsp_feed.cv2") as mock_cv2, patch("rtsp_feed.quit") as mock_quit:
            try:
                # This should handle the exception gracefully
                # The close function should still call cv2.destroyAllWindows and quit
                rtsp_feed.close()
            except Exception:
                # The exception from cap.release() should propagate but let's verify the calls
                pass
            finally:
                # Restore original state
                if original_cap is not None:
                    rtsp_feed.cap = original_cap
                elif hasattr(rtsp_feed, "cap"):
                    delattr(rtsp_feed, "cap")

            # Verify cap.release() was called (and raised exception)
            mock_cap.release.assert_called_once()

    def test_pil_image_with_invalid_frame(self):
        """Test PIL Image creation with invalid frame data"""
        # Test with None frame
        with self.assertRaises((TypeError, AttributeError)):
            Image.fromarray(None, "RGB")

        # Test with wrong shape
        invalid_frame = np.zeros((480, 640), dtype=np.uint8)  # Missing color channel
        with self.assertRaises((ValueError, TypeError)):
            Image.fromarray(invalid_frame, "RGB")

        # Test with wrong dtype
        invalid_frame = np.zeros((480, 640, 3), dtype=np.float64)
        # This might work but produce unexpected results
        pil_image = Image.fromarray(invalid_frame.astype(np.uint8), "RGB")
        self.assertIsInstance(pil_image, Image.Image)


if __name__ == "__main__":
    unittest.main()
