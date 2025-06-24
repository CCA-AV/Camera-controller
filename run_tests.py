#!/usr/bin/env python3
"""
Simple test runner for Camera Controller tests.
This script can run the tests without requiring pytest installation.
"""

import sys
import os
import unittest
from unittest.mock import Mock, patch

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import test modules
try:
    from tests.test_camera import TestCamera, TestCameraEdgeCases
    from tests.test_visca_integration import TestViscaIntegration

    print("✓ Successfully imported test modules")
except ImportError as e:
    print(f"✗ Failed to import test modules: {e}")
    print("Make sure you're running this from the project root directory")
    sys.exit(1)


def run_basic_tests():
    """Run basic tests to verify the test framework works"""
    print("\n" + "=" * 60)
    print("RUNNING BASIC CAMERA TESTS")
    print("=" * 60)

    # Create a simple test to verify mocking works
    try:
        with patch("socket.socket") as mock_socket_class:
            mock_socket = Mock()
            mock_socket.recv.return_value = bytes.fromhex("9041ff")
            mock_socket_class.return_value = mock_socket

            from controller import Camera

            cam = Camera()

            # Test that camera initializes with mock
            assert cam.socket == mock_socket
            assert mock_socket.connect.called
            print("✓ Camera initialization with mock socket: PASSED")

            # Test basic command execution
            result = cam.execute("8101040002ff")
            assert result == "9041ff"
            print("✓ Basic command execution: PASSED")

            # Test power on command
            with patch.object(cam, "run") as mock_run:
                cam.on()
                mock_run.assert_called_once()
                print("✓ Power on command: PASSED")

            # Test zoom command with parameter substitution
            with patch.object(cam, "run") as mock_run:
                cam.zoom("direct", 1000)
                # Verify the run method was called (actual command validation in full tests)
                mock_run.assert_called_once()
                print("✓ Zoom command with parameters: PASSED")

            print("\n✓ All basic tests PASSED!")

    except Exception as e:
        print(f"✗ Basic test failed: {e}")
        return False

    return True


def run_visca_validation():
    """Run VISCA command validation tests"""
    print("\n" + "=" * 60)
    print("RUNNING VISCA COMMAND VALIDATION")
    print("=" * 60)

    try:
        import visca

        # Test command format validation
        command_count = 0
        for command_name, command_hex in visca.commands.items():
            if isinstance(command_hex, str):  # Skip nested dicts
                assert command_hex.startswith(
                    "81"
                ), f"Command {command_name} should start with 81"
                assert command_hex.endswith(
                    "ff"
                ), f"Command {command_name} should end with ff"
                assert (
                    len(command_hex) % 2 == 0
                ), f"Command {command_name} should have even length"
                command_count += 1

        print(f"✓ Validated {command_count} VISCA commands format")

        # Test inquiry command format validation
        inquiry_count = 0
        for command_name, command_hex in visca.commands["inq"].items():
            if command_hex:  # Skip empty commands
                assert command_hex.startswith(
                    "8109"
                ), f"Inquiry {command_name} should start with 8109"
                assert command_hex.endswith(
                    "ff"
                ), f"Inquiry {command_name} should end with ff"
                assert (
                    len(command_hex) % 2 == 0
                ), f"Inquiry {command_name} should have even length"
                inquiry_count += 1

        print(f"✓ Validated {inquiry_count} VISCA inquiry commands format")

        # Test parameter substitution
        zoom_cmd = visca.commands["zoom_direct"]
        test_result = zoom_cmd.replace("p", "12345678")
        expected = "8101044712345678ff"
        assert (
            test_result == expected
        ), f"Parameter substitution failed: {test_result} != {expected}"
        print("✓ Parameter substitution validation: PASSED")

        print("\n✓ All VISCA validation tests PASSED!")

    except Exception as e:
        print(f"✗ VISCA validation failed: {e}")
        return False

    return True


def main():
    """Main test runner"""
    print("Camera Controller Test Runner")
    print("Testing without pytest dependency")

    success = True

    # Run basic functionality tests
    if not run_basic_tests():
        success = False

    # Run VISCA validation tests
    if not run_visca_validation():
        success = False

    print("\n" + "=" * 60)
    if success:
        print("🎉 ALL TESTS PASSED!")
        print("\nFor more comprehensive testing, install pytest and run:")
        print("  pip install pytest")
        print("  python -m pytest tests/ -v")
    else:
        print("❌ SOME TESTS FAILED!")
        print("Check the error messages above for details.")
    print("=" * 60)

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
