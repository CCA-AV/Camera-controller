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
    from tests.test_vcapture import (
        TestVcaptureInit,
        TestVcaptureProperties,
        TestVcaptureRun,
        TestVcaptureRelease,
    )
    from tests.test_rtsp_feed import (
        TestRtspFeedClose,
        TestRtspFeedIntegration,
        TestRtspFeedFrameProcessing,
        TestRtspFeedConstants,
        TestRtspFeedMocks,
        TestRtspFeedMainExecution,
        TestRtspFeedErrorHandling,
    )

    print("[OK] Successfully imported test modules")
except ImportError as e:
    print(f"[ERROR] Failed to import test modules: {e}")
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
            print("[OK] Camera initialization with mock socket: PASSED")

            # Test basic command execution
            result = cam.execute("8101040002ff")
            assert result == "9041ff"
            print("[OK] Basic command execution: PASSED")

            # Test power on command
            with patch.object(cam, "run") as mock_run:
                cam.on()
                mock_run.assert_called_once()
                print("[OK] Power on command: PASSED")

            # Test zoom command with parameter substitution
            with patch.object(cam, "run") as mock_run:
                cam.zoom("direct", 1000)
                # Verify the run method was called (actual command validation in full tests)
                mock_run.assert_called_once()
                print("[OK] Zoom command with parameters: PASSED")

            print("\n[OK] All basic tests PASSED!")

    except Exception as e:
        print(f"[FAIL] Basic test failed: {e}")
        return False

    return True


def run_visca_validation():
    """Run VISCA command validation tests"""
    print("\n" + "=" * 60)
    print("RUNNING VISCA COMMAND VALIDATION")
    print("=" * 60)

    try:
        from controller import Camera
        from visca import ViscaParser
        import inspect

        # Get the default camera type from Camera class constructor
        camera_signature = inspect.signature(Camera.__init__)
        default_camera_type = camera_signature.parameters["camera_type"].default
        print(f"[OK] Using camera type: {default_camera_type}")

        # Create ViscaParser with the default camera type
        parser = ViscaParser(default_camera_type)
        commands = parser.commands
        returns = parser.returns

        # Test command format validation
        command_count = 0
        for command_name, command_data in commands.items():
            if (
                isinstance(command_data, dict) and "command" in command_data
            ):  # New dict format
                command_hex = command_data["command"]
                assert command_hex.startswith(
                    "81"
                ), f"Command {command_name} should start with 81"
                assert command_hex.endswith(
                    "ff"
                ), f"Command {command_name} should end with ff"
                # Skip length check for template commands that contain placeholders
                if not any(
                    placeholder in command_hex
                    for placeholder in [
                        "p",
                        "q",
                        "r",
                        "s",
                        "P",
                        "Q",
                        "R",
                        "S",
                        "V",
                        "W",
                        "A",
                        "B",
                        "C",
                        "D",
                        "T",
                    ]
                ):
                    assert (
                        len(command_hex) % 2 == 0
                    ), f"Command {command_name} should have even length (valid hex)"
                command_count += 1
            elif isinstance(command_data, str):  # Legacy string format (skip for now)
                pass  # Skip string commands - they're legacy or special cases

        print(f"[OK] Validated {command_count} VISCA commands format")

        # Test inquiry command format validation
        inquiry_count = 0
        for command_name, command_hex in commands["inq"].items():
            if command_hex:  # Skip empty commands
                # Some special commands may start with different prefixes
                if command_name not in ["enlargement_block"]:  # Special case
                    assert command_hex.startswith(
                        "8109"
                    ), f"Inquiry {command_name} should start with 8109"
                assert command_hex.endswith(
                    "ff"
                ), f"Inquiry {command_name} should end with ff"
                # Skip length check for template commands that contain placeholders
                if not any(
                    placeholder in command_hex
                    for placeholder in [
                        "p",
                        "q",
                        "r",
                        "s",
                        "P",
                        "Q",
                        "R",
                        "S",
                        "V",
                        "W",
                        "A",
                        "B",
                        "C",
                        "D",
                        "T",
                    ]
                ):
                    assert (
                        len(command_hex) % 2 == 0
                    ), f"Inquiry {command_name} should have even length"
                inquiry_count += 1

        print(f"[OK] Validated {inquiry_count} VISCA inquiry commands format")

        # Test parameter substitution using the command builder
        from controller import Camera

        cam = Camera()
        test_result = cam.build_command("zoom_direct", 1000)  # Simple test value
        expected = "81010447000003e8ff"  # 1000 in hex = 3e8, padded to 8 chars
        assert (
            test_result == expected
        ), f"Parameter substitution failed: {test_result} != {expected}"
        print("[OK] Parameter substitution validation: PASSED")

        print("\n[OK] All VISCA validation tests PASSED!")

    except Exception as e:
        print(f"[FAIL] VISCA validation failed: {e}")
        return False

    return True


def run_vcapture_tests():
    """Run vcapture module tests"""
    print("\n" + "=" * 60)
    print("RUNNING VCAPTURE TESTS")
    print("=" * 60)

    try:
        # Create a test suite for vcapture tests
        loader = unittest.TestLoader()
        suite = unittest.TestSuite()

        # Add all vcapture test classes
        suite.addTests(loader.loadTestsFromTestCase(TestVcaptureInit))
        suite.addTests(loader.loadTestsFromTestCase(TestVcaptureProperties))
        suite.addTests(loader.loadTestsFromTestCase(TestVcaptureRun))
        suite.addTests(loader.loadTestsFromTestCase(TestVcaptureRelease))

        # Run the tests
        runner = unittest.TextTestRunner(verbosity=1, stream=sys.stdout)
        result = runner.run(suite)

        if result.wasSuccessful():
            print("[OK] All vcapture tests PASSED!")
            return True
        else:
            print(
                f"[FAIL] vcapture tests FAILED: {len(result.failures)} failures, {len(result.errors)} errors"
            )
            return False

    except Exception as e:
        print(f"[FAIL] vcapture test execution failed: {e}")
        return False


def run_rtsp_feed_tests():
    """Run rtsp_feed module tests"""
    print("\n" + "=" * 60)
    print("RUNNING RTSP FEED TESTS")
    print("=" * 60)

    try:
        # Create a test suite for rtsp_feed tests
        loader = unittest.TestLoader()
        suite = unittest.TestSuite()

        # Add all rtsp_feed test classes
        suite.addTests(loader.loadTestsFromTestCase(TestRtspFeedClose))
        suite.addTests(loader.loadTestsFromTestCase(TestRtspFeedIntegration))
        suite.addTests(loader.loadTestsFromTestCase(TestRtspFeedFrameProcessing))
        suite.addTests(loader.loadTestsFromTestCase(TestRtspFeedConstants))
        suite.addTests(loader.loadTestsFromTestCase(TestRtspFeedMocks))
        suite.addTests(loader.loadTestsFromTestCase(TestRtspFeedMainExecution))
        suite.addTests(loader.loadTestsFromTestCase(TestRtspFeedErrorHandling))

        # Run the tests
        runner = unittest.TextTestRunner(verbosity=1, stream=sys.stdout)
        result = runner.run(suite)

        if result.wasSuccessful():
            print("[OK] All rtsp_feed tests PASSED!")
            return True
        else:
            print(
                f"[FAIL] rtsp_feed tests FAILED: {len(result.failures)} failures, {len(result.errors)} errors"
            )
            return False

    except Exception as e:
        print(f"[FAIL] rtsp_feed test execution failed: {e}")
        return False


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

    # Run vcapture tests
    if not run_vcapture_tests():
        success = False

    # Run rtsp_feed tests
    if not run_rtsp_feed_tests():
        success = False

    print("\n" + "=" * 60)
    if success:
        print("[OK] ALL TESTS PASSED!")
        print("\nFor more comprehensive testing, install pytest and run:")
        print("  pip install pytest")
        print("  python -m pytest tests/ -v")
    else:
        print("[FAIL] SOME TESTS FAILED!")
        print("Check the error messages above for details.")
    print("=" * 60)

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
