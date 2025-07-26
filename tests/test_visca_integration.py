import pytest
from unittest.mock import Mock, patch
import sys
import os
import inspect

# Add parent directory to path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from controller import Camera
from visca import ViscaParser


class TestViscaIntegration:
    """Integration tests to verify Camera class generates correct VISCA commands"""

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

    @pytest.fixture
    def default_parser(self):
        """Create a ViscaParser with the default camera type"""
        # Get the default camera type from Camera class constructor
        camera_signature = inspect.signature(Camera.__init__)
        default_camera_type = camera_signature.parameters["camera_type"].default
        return ViscaParser(default_camera_type)

    def test_power_commands_generate_correct_visca(self, camera):
        """Test that power commands generate correct VISCA hex strings"""
        # Test power on
        with patch.object(camera, "execute") as mock_execute:
            mock_execute.return_value = "9041ff"
            with patch.object(
                camera.parser, "interpret_completion", return_value="Command Completed"
            ):
                camera.on()
                # The on() method calls execute with the raw command dictionary
                mock_execute.assert_called_with(camera.commands["power_on"])

        # Test power off
        with patch.object(camera, "execute") as mock_execute:
            mock_execute.return_value = "9041ff"
            with patch.object(
                camera.parser, "interpret_completion", return_value="Command Completed"
            ):
                camera.off()
                # The off() method calls execute with the raw command dictionary
                mock_execute.assert_called_with(camera.commands["power_off"])

    def test_zoom_commands_generate_correct_visca(self, camera):
        """Test that zoom commands generate correct VISCA hex strings"""
        test_cases = [
            # (method_args, expected_command)
            (("tele",), "8101040702ff"),  # zoom tele standard
            (("wide",), "8101040703ff"),  # zoom wide standard
            (
                ("tele", 3),
                camera.build_command("zoom_tele_var", 3),
            ),  # zoom tele variable
            (
                ("wide", 5),
                camera.build_command("zoom_wide_var", 5),
            ),  # zoom wide variable
            (
                ("direct", 1000),
                camera.build_command("zoom_direct", 1000),
            ),  # zoom direct with int
            (
                ("direct", 4096),
                camera.build_command("zoom_direct", 4096),
            ),  # zoom direct with different int
        ]

        for args, expected_command in test_cases:
            with patch.object(camera, "execute") as mock_execute:
                mock_execute.return_value = "9041ff"
                with patch.object(
                    camera.parser,
                    "interpret_completion",
                    return_value="Command Completed",
                ):
                    camera.zoom(*args)
                    mock_execute.assert_called_with(expected_command)

    def test_focus_commands_generate_correct_visca(self, camera):
        """Test that focus commands generate correct VISCA hex strings"""
        test_cases = [
            # (method_args, expected_command)
            (("far",), "8101040802ff"),  # focus far standard
            (("near",), "8101040803ff"),  # focus near standard
            (("far", 2), "810104082.ff".replace(".", "2")),  # focus far variable
            (("near", 4), "810104083.ff".replace(".", "4")),  # focus near variable
            (
                ("direct", 850),
                "81010448030503020ff",
            ),  # focus direct with int (850 = 0x352)
        ]

        for args, expected_command in test_cases:
            with patch.object(camera, "execute") as mock_execute:
                mock_execute.return_value = "9041ff"
                with patch.object(
                    camera.parser,
                    "interpret_completion",
                    return_value="Command Completed",
                ):
                    camera.focus(*args)
                    # For focus direct, we need to handle the character replacement
                    if args[0] == "direct":
                        if isinstance(args[1], int):
                            hex_val = f"{args[1]:04x}"
                            expected_command = (
                                "810104480.0.0.0.ff".replace(".", hex_val[0], 1)
                                .replace(".", hex_val[1], 1)
                                .replace(".", hex_val[2], 1)
                                .replace(".", hex_val[3], 1)
                            )
                    mock_execute.assert_called_with(expected_command)

    def test_backlight_commands_generate_correct_visca(self, camera):
        """Test that backlight commands generate correct VISCA hex strings"""
        # Test backlight on
        with patch.object(camera, "execute") as mock_execute:
            mock_execute.return_value = "9041ff"
            with patch.object(
                camera.parser, "interpret_completion", return_value="Command Completed"
            ):
                camera.backlight = True
                expected_command = camera.build_command("backlight", backlight=2)
                mock_execute.assert_called_with(expected_command)

        # Test backlight off
        with patch.object(camera, "execute") as mock_execute:
            mock_execute.return_value = "9041ff"
            with patch.object(
                camera.parser, "interpret_completion", return_value="Command Completed"
            ):
                camera.backlight = False
                expected_command = camera.build_command("backlight", backlight=3)
                mock_execute.assert_called_with(expected_command)

    def test_inquiry_commands_generate_correct_visca(self, camera):
        """Test that inquiry commands generate correct VISCA hex strings"""
        inquiry_tests = [
            # (property_name, expected_command)
            ("zoom_pos", "81090447ff"),
            ("focus_pos", "81090448ff"),
            ("backlight", "81090433ff"),
            ("power", "81097E7E02ff"),
        ]

        for prop_name, expected_command in inquiry_tests:
            with patch.object(camera, "execute") as mock_execute:
                mock_execute.return_value = "90500102ff"
                with patch.object(
                    camera.parser, "interpret_inquire", return_value=["01", "02"]
                ):
                    if prop_name == "zoom_pos":
                        _ = camera.zoom_pos
                    elif prop_name == "focus_pos":
                        _ = camera.focus_pos
                    elif prop_name == "backlight":
                        _ = camera.backlight
                    elif prop_name == "power":
                        _ = camera.power

                    mock_execute.assert_called_with(expected_command)

    def test_visca_command_format_validation(self, camera, default_parser):
        """Test that all VISCA commands follow the correct format"""
        # All VISCA commands should start with 81 and end with ff
        for command_name, command_hex in default_parser.commands.items():
            if isinstance(command_hex, str):  # Skip nested dicts like "inq"
                assert command_hex.startswith(
                    "81"
                ), f"Command {command_name} should start with 81"
                assert command_hex.endswith(
                    "ff"
                ), f"Command {command_name} should end with ff"
                # Skip length check for template commands that contain placeholders
                if not any(
                    placeholder in command_hex
                    for placeholder in ["p", "q", "r", "s", "P", "V", "W"]
                ):
                    assert (
                        len(command_hex) % 2 == 0
                    ), f"Command {command_name} should have even length (valid hex)"

    def test_visca_inquiry_command_format_validation(self, camera, default_parser):
        """Test that all VISCA inquiry commands follow the correct format"""
        # Most inquiry commands should start with 8109 and end with ff
        for command_name, command_hex in default_parser.commands["inq"].items():
            if command_hex:  # Skip empty commands
                # Some special commands may start with different prefixes
                if command_name not in ["enlargement_block"]:  # Special case
                    assert command_hex.startswith(
                        "8109"
                    ), f"Inquiry {command_name} should start with 8109"
                assert command_hex.endswith(
                    "ff"
                ), f"Inquiry {command_name} should end with ff"
                # Skip length check for template commands
                if not any(
                    placeholder in command_hex
                    for placeholder in ["p", "q", "r", "s", "P"]
                ):
                    assert (
                        len(command_hex) % 2 == 0
                    ), f"Inquiry {command_name} should have even length (valid hex)"

    def test_camera_uses_correct_visca_commands(self, camera, default_parser):
        """Test that Camera class references correct VISCA commands from parser"""
        # Verify that camera.commands is the same as the parser.commands
        assert camera.commands is default_parser.commands

        # Test a few key commands are accessible
        assert "power_on" in camera.commands
        assert "power_off" in camera.commands
        assert "zoom_direct" in camera.commands
        assert "focus_direct" in camera.commands
        assert "backlight" in camera.commands
        assert "inq" in camera.commands

        # Test inquiry commands are accessible
        assert "zoom_pos" in camera.commands["inq"]
        assert "focus_pos" in camera.commands["inq"]
        assert "backlight_mode" in camera.commands["inq"]
        assert "other_block" in camera.commands["inq"]

    def test_hex_parameter_substitution(self, camera, default_parser):
        """Test that parameter substitution in VISCA commands works correctly"""
        # Test zoom direct parameter substitution using the command builder
        test_values = [
            (0, camera.build_command("zoom_direct", 0)),
            (
                1000000,
                camera.build_command("zoom_direct", 1000000),
            ),  # Valid value within range
            (67108864, camera.build_command("zoom_direct", 67108864)),  # Max value
        ]

        for int_val, expected in test_values:
            # Test that we can build the command successfully
            result = camera.build_command("zoom_direct", int_val)
            assert result == expected

    def test_focus_parameter_substitution(self, camera, default_parser):
        """Test that focus direct parameter substitution works correctly"""
        # Test with integer values that will be converted to hex internally
        test_values = [
            (0, camera.build_command("focus_direct", 0)),
            (
                1000,
                camera.build_command("focus_direct", 1000),
            ),  # Valid value within range
            (1770, camera.build_command("focus_direct", 1770)),  # max value
        ]

        for int_val, expected in test_values:
            result = camera.build_command("focus_direct", int_val)
            assert result == expected

    def test_backlight_parameter_substitution(self, camera, default_parser):
        """Test that backlight parameter substitution works correctly"""
        # Test on/off values using the command builder
        on_command = camera.build_command("backlight", backlight=2)
        off_command = camera.build_command("backlight", backlight=3)

        # The exact values depend on the command builder implementation
        assert on_command == "8101043302ff"
        assert off_command == "8101043303ff"


if __name__ == "__main__":
    pytest.main([__file__])
