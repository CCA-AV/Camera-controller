import pytest
import socket
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add parent directory to path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from controller import Camera


class TestCamera:
    """Test suite for the Camera class"""

    @pytest.fixture
    def mock_socket(self):
        """Create a mock socket for testing"""
        mock_sock = Mock()
        mock_sock.recv.return_value = bytes.fromhex(
            "9041ff"
        )  # Default "Command Accepted" response
        return mock_sock

    @pytest.fixture
    def camera(self, mock_socket):
        """Create a Camera instance with mocked socket"""
        with patch("socket.socket") as mock_socket_class:
            mock_socket_class.return_value = mock_socket
            cam = Camera(ip="192.168.0.25", port=1259)
            cam.socket = mock_socket
            return cam

    def test_camera_initialization(self, mock_socket):
        """Test camera initialization with correct parameters"""
        with patch("socket.socket") as mock_socket_class:
            mock_socket_class.return_value = mock_socket
            cam = Camera(ip="192.168.0.25", port=1259)

            # Verify socket was created and connected
            mock_socket_class.assert_called_once_with(
                socket.AF_INET, socket.SOCK_DGRAM, 0
            )
            mock_socket.connect.assert_called_once_with(("192.168.0.25", 1259))

            # Verify camera has access to VISCA commands via parser
            assert cam.commands is not None
            assert cam.parser is not None

    def test_camera_initialization_default_params(self, mock_socket):
        """Test camera initialization with default parameters"""
        with patch("socket.socket") as mock_socket_class:
            mock_socket_class.return_value = mock_socket
            cam = Camera()

            # Verify default connection parameters
            mock_socket.connect.assert_called_once_with(("192.168.0.25", 1259))

    def test_close_method(self, camera):
        """Test the close method properly closes the socket"""
        camera.close()
        camera.socket.close.assert_called_once()

    def test_execute_method(self, camera):
        """Test the execute method sends correct hex command and returns response"""
        # Setup mock response
        camera.socket.recv.return_value = bytes.fromhex("9041ff")

        # Test command execution
        result = camera.execute("8101040002ff")

        # Verify command was sent as bytes
        camera.socket.send.assert_called_once_with(bytes.fromhex("8101040002ff"))

        # Verify response was received and converted to hex
        camera.socket.recv.assert_called_once_with(256)
        assert result == "9041ff"

    def test_power_on_command(self, camera):
        """Test power on command sends correct VISCA command"""
        with patch.object(camera, "run") as mock_run:
            camera.on()
            mock_run.assert_called_once_with(camera.commands["power_on"])

    def test_power_off_command(self, camera):
        """Test power off command sends correct VISCA command"""
        with patch.object(camera, "run") as mock_run:
            camera.off()
            mock_run.assert_called_once_with(camera.commands["power_off"])

    def test_power_property_inquiry(self, camera):
        """Test power property queries the correct VISCA inquiry command"""
        with patch.object(camera, "inquire") as mock_inquire:
            mock_inquire.return_value = [1]  # Power on

            result = camera.power

            mock_inquire.assert_called_once_with(camera.commands["inq"]["other_block"])

    def test_backlight_property_inquiry(self, camera):
        """Test backlight property queries the correct VISCA inquiry command"""
        with patch.object(camera, "inquire") as mock_inquire:
            mock_inquire.return_value = [2]  # Backlight on

            result = camera.backlight

            mock_inquire.assert_called_once_with(
                camera.commands["inq"]["backlight_mode"]
            )

    def test_backlight_setter(self, camera):
        """Test backlight setter sends correct VISCA command"""
        with patch.object(camera, "run") as mock_run:
            # Test setting backlight on
            camera.backlight = True
            expected_command = camera.commands["backlight"].replace("P", "2")
            mock_run.assert_called_with(expected_command)

            # Test setting backlight off
            camera.backlight = False
            expected_command = camera.commands["backlight"].replace("P", "3")
            mock_run.assert_called_with(expected_command)

    def test_zoom_pos_property(self, camera):
        """Test zoom position property queries correct VISCA inquiry command"""
        with patch.object(camera, "inquire") as mock_inquire:
            mock_inquire.return_value = ["1000"]  # Mock zoom position

            result = camera.zoom_pos

            mock_inquire.assert_called_once_with(camera.commands["inq"]["zoom_pos"])

    def test_zoom_pos_setter(self, camera):
        """Test zoom position setter calls zoom method correctly"""
        with patch.object(camera, "zoom") as mock_zoom:
            camera.zoom_pos = "2080309"
            mock_zoom.assert_called_once_with("direct", "2080309")

    def test_focus_pos_property(self, camera):
        """Test focus position property queries correct VISCA inquiry command"""
        with patch.object(camera, "inquire") as mock_inquire:
            mock_inquire.return_value = ["0500"]  # Mock focus position

            result = camera.focus_pos

            mock_inquire.assert_called_once_with(camera.commands["inq"]["focus_pos"])

    def test_focus_pos_setter(self, camera):
        """Test focus position setter calls focus method correctly"""
        with patch.object(camera, "focus") as mock_focus:
            camera.focus_pos = 850
            mock_focus.assert_called_once_with("direct", 850)

    def test_zoom_direct_int_value(self, camera):
        """Test zoom direct method with integer value"""
        with patch.object(camera, "run") as mock_run:
            camera.zoom("direct", 1000)

            # Integer should be converted to hex and padded to 8 digits
            expected_command = camera.commands["zoom_direct"].replace("p", "000003e8")
            mock_run.assert_called_once_with(expected_command)

    def test_zoom_direct_hex_string_value(self, camera):
        """Test zoom direct method with hex string value"""
        with patch.object(camera, "run") as mock_run:
            camera.zoom("direct", "2080309")

            # Hex string should be padded to 8 digits
            expected_command = camera.commands["zoom_direct"].replace("p", "02080309")
            mock_run.assert_called_once_with(expected_command)

    def test_zoom_tele_standard(self, camera):
        """Test zoom tele standard speed"""
        with patch.object(camera, "run") as mock_run:
            camera.zoom("tele")
            mock_run.assert_called_once_with(camera.commands["zoom_tele_std"])

    def test_zoom_tele_variable(self, camera):
        """Test zoom tele variable speed"""
        with patch.object(camera, "run") as mock_run:
            camera.zoom("tele", 5)
            expected_command = camera.commands["zoom_tele_var"].replace("p", "5")
            mock_run.assert_called_once_with(expected_command)

    def test_zoom_wide_standard(self, camera):
        """Test zoom wide standard speed"""
        with patch.object(camera, "run") as mock_run:
            camera.zoom("wide")
            mock_run.assert_called_once_with(camera.commands["zoom_wide_std"])

    def test_zoom_wide_variable(self, camera):
        """Test zoom wide variable speed"""
        with patch.object(camera, "run") as mock_run:
            camera.zoom("wide", 3)
            expected_command = camera.commands["zoom_wide_var"].replace("p", "3")
            mock_run.assert_called_once_with(expected_command)

    def test_focus_direct_int_value(self, camera):
        """Test focus direct method with integer value"""
        with patch.object(camera, "run") as mock_run:
            camera.focus("direct", 850)

            # Integer should be converted to hex and formatted correctly
            hex_val = "0352"  # 850 in hex, padded to 4 digits
            expected_command = (
                camera.commands["focus_direct"]
                .replace("p", hex_val[0])
                .replace("q", hex_val[1])
                .replace("r", hex_val[2])
                .replace("s", hex_val[3])
            )
            mock_run.assert_called_once_with(expected_command)

    def test_focus_direct_hex_string_value(self, camera):
        """Test focus direct method with hex string value"""
        with patch.object(camera, "run") as mock_run:
            camera.focus("direct", "abc")

            # Hex string should be padded to 4 digits
            hex_val = "0abc"
            expected_command = (
                camera.commands["focus_direct"]
                .replace("p", hex_val[0])
                .replace("q", hex_val[1])
                .replace("r", hex_val[2])
                .replace("s", hex_val[3])
            )
            mock_run.assert_called_once_with(expected_command)

    def test_focus_far_standard(self, camera):
        """Test focus far standard speed"""
        with patch.object(camera, "run") as mock_run:
            camera.focus("far")
            mock_run.assert_called_once_with(camera.commands["focus_far_std"])

    def test_focus_far_variable(self, camera):
        """Test focus far variable speed"""
        with patch.object(camera, "run") as mock_run:
            camera.focus("far", 4)
            expected_command = camera.commands["focus_far_var"].replace("p", "4")
            mock_run.assert_called_once_with(expected_command)

    def test_focus_near_standard(self, camera):
        """Test focus near standard speed"""
        with patch.object(camera, "run") as mock_run:
            camera.focus("near")
            mock_run.assert_called_once_with(camera.commands["focus_near_std"])

    def test_focus_near_variable(self, camera):
        """Test focus near variable speed"""
        with patch.object(camera, "run") as mock_run:
            camera.focus("near", 2)
            expected_command = camera.commands["focus_near_var"].replace("p", "2")
            mock_run.assert_called_once_with(expected_command)

    def test_run_method_command_completion(self, camera):
        """Test run method executes command and returns interpretation"""
        with patch.object(camera, "execute") as mock_execute:
            with patch.object(camera.parser, "interpret_completion") as mock_interpret:
                mock_execute.return_value = "9051ff"  # Command Completed
                mock_interpret.return_value = "Command Completed"

                result = camera.run("8101040002ff")

                # Should have called execute once
                mock_execute.assert_called_once_with("8101040002ff")
                # Should have called interpret_completion with the result
                mock_interpret.assert_called_with("9051ff")
                assert result == "Command Completed"

    def test_inquire_method(self, camera):
        """Test inquire method calls correct VISCA interpretation"""
        camera.socket.recv.return_value = bytes.fromhex("90500102ff")

        with patch.object(camera.parser, "interpret_inquire") as mock_interpret:
            mock_interpret.return_value = ["01", "02"]

            result = camera.inquire("81090447ff")

            # Verify command was sent
            camera.socket.send.assert_called_once_with(bytes.fromhex("81090447ff"))

            # Verify interpretation was called with response
            mock_interpret.assert_called_once_with("90500102ff")

            assert result == ["01", "02"]

    def test_restart_method(self, camera):
        """Test restart method calls off and on"""
        with patch.object(camera, "off") as mock_off:
            with patch.object(camera, "on") as mock_on:
                # Mock the power property inquiry to return False (off)
                with patch.object(camera, "inquire", return_value=[0]):  # 0 = power off
                    camera.restart()

                    mock_off.assert_called_once()
                    mock_on.assert_called_once()

    def test_brightness_property_queries_camera(self, camera):
        """Test brightness property queries camera and returns inquiry result"""
        # The brightness property now properly queries the camera with caching
        with patch.object(camera, "inquire") as mock_inquire:
            mock_inquire.return_value = ["0a", "0b"]  # Mock brightness inquiry result

            result = camera.brightness

            # Verify it called inquire with correct command
            mock_inquire.assert_called_once_with(camera.commands["inq"]["brightness"])

            # Verify it returns the inquiry result
            assert result == ["0a", "0b"]

    def test_check_method_sends_empty_command(self, camera):
        """Test check method sends empty command and returns response"""
        camera.socket.recv.return_value = bytes.fromhex("9051ff")

        result = camera.check()

        # Should send empty bytes
        camera.socket.send.assert_called_once_with(bytes.fromhex(""))
        assert result == "9051ff"


class TestCameraEdgeCases:
    """Test edge cases and error conditions"""

    @pytest.fixture
    def camera(self):
        """Create a Camera instance with mocked socket"""
        with patch("socket.socket") as mock_socket_class:
            mock_socket = Mock()
            mock_socket.recv.return_value = bytes.fromhex("9041ff")
            mock_socket_class.return_value = mock_socket
            cam = Camera()
            cam.socket = mock_socket
            return cam

    def test_zoom_direct_with_max_value(self, camera):
        """Test zoom direct with maximum value"""
        with patch.object(camera, "run") as mock_run:
            # Test with maximum zoom value (67108864 decimal = 4000000 hex)
            camera.zoom("direct", 67108864)
            expected_command = camera.commands["zoom_direct"].replace("p", "04000000")
            mock_run.assert_called_once_with(expected_command)

    def test_zoom_direct_with_zero_value(self, camera):
        """Test zoom direct with zero value"""
        with patch.object(camera, "run") as mock_run:
            camera.zoom("direct", 0)
            expected_command = camera.commands["zoom_direct"].replace("p", "00000000")
            mock_run.assert_called_once_with(expected_command)

    def test_focus_direct_with_max_value(self, camera):
        """Test focus direct with maximum value"""
        with patch.object(camera, "run") as mock_run:
            # Test with maximum focus value (1770 decimal = 6EA hex)
            camera.focus("direct", 1770)
            hex_val = "06ea"
            expected_command = (
                camera.commands["focus_direct"]
                .replace("p", hex_val[0])
                .replace("q", hex_val[1])
                .replace("r", hex_val[2])
                .replace("s", hex_val[3])
            )
            mock_run.assert_called_once_with(expected_command)

    def test_focus_direct_with_zero_value(self, camera):
        """Test focus direct with zero value"""
        with patch.object(camera, "run") as mock_run:
            camera.focus("direct", 0)
            expected_command = (
                camera.commands["focus_direct"]
                .replace("p", "0")
                .replace("q", "0")
                .replace("r", "0")
                .replace("s", "0")
            )
            mock_run.assert_called_once_with(expected_command)

    def test_zoom_variable_speed_bounds(self, camera):
        """Test zoom variable speed with boundary values"""
        with patch.object(camera, "run") as mock_run:
            # Test minimum speed
            camera.zoom("tele", 0)
            expected_command = camera.commands["zoom_tele_var"].replace("p", "0")
            mock_run.assert_called_with(expected_command)

            # Test maximum speed
            camera.zoom("wide", 7)
            expected_command = camera.commands["zoom_wide_var"].replace("p", "7")
            mock_run.assert_called_with(expected_command)

    def test_focus_variable_speed_bounds(self, camera):
        """Test focus variable speed with boundary values"""
        with patch.object(camera, "run") as mock_run:
            # Test minimum speed
            camera.focus("far", 0)
            expected_command = camera.commands["focus_far_var"].replace("p", "0")
            mock_run.assert_called_with(expected_command)

            # Test maximum speed
            camera.focus("near", 7)
            expected_command = camera.commands["focus_near_var"].replace("p", "7")
            mock_run.assert_called_with(expected_command)


if __name__ == "__main__":
    pytest.main([__file__])
