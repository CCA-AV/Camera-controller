import pytest
import socket
from unittest.mock import Mock, patch, MagicMock, call
import sys
import os

# Add parent directory to path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from controller import Camera
import visca


class TestCachingSystem:
    """Test suite for the Camera class caching system"""

    @pytest.fixture
    def mock_socket(self):
        """Create a mock socket for testing"""
        mock_sock = Mock()
        mock_sock.recv.return_value = bytes.fromhex(
            "905000000a0bff"
        )  # Mock inquiry response
        return mock_sock

    @pytest.fixture
    def camera(self, mock_socket):
        """Create a Camera instance with mocked socket"""
        with patch("socket.socket") as mock_socket_class:
            mock_socket_class.return_value = mock_socket
            cam = Camera(ip="192.168.0.25", port=1259)
            cam.socket = mock_socket
            return cam

    def test_cache_initialization(self, camera):
        """Test that cache is properly initialized"""
        # Cache should start empty
        cache_info = camera.get_cache_info()
        assert len(cache_info) == 0

        # Cache timeout should be 200ms (0.2 seconds)
        assert camera._cache_timeout == 0.2

    def test_cache_hit_prevents_duplicate_inquiries(self, camera):
        """Test that cached values prevent duplicate camera inquiries"""
        # Setup mock response
        camera.socket.recv.return_value = bytes.fromhex("905000000a0bff")

        with patch("visca.interpret_inquire") as mock_interpret:
            mock_interpret.return_value = ["0a", "0b"]

            # First call - should query camera
            brightness1 = camera.brightness
            first_call_count = camera.socket.send.call_count

            # Second call immediately - should use cache, no additional query
            brightness2 = camera.brightness
            second_call_count = camera.socket.send.call_count

            # Verify no additional camera query was made
            assert second_call_count == first_call_count

            # Verify same result returned
            assert brightness1 == brightness2

    def test_cache_expiration_triggers_new_inquiry(self, camera):
        """Test that expired cache triggers new camera inquiry"""
        camera.socket.recv.return_value = bytes.fromhex("905000000a0bff")

        with patch("visca.interpret_inquire") as mock_interpret:
            mock_interpret.return_value = ["0a", "0b"]

            with patch.object(
                camera, "_get_cached_value", wraps=camera._get_cached_value
            ) as mock_get_cached:
                # Mock time progression in the cache methods
                with patch("time.time") as mock_time:
                    mock_time.return_value = 1000.0

                    # First call - cache miss
                    brightness1 = camera.brightness
                    first_call_count = camera.socket.send.call_count

                    # Second call immediately - cache hit
                    brightness2 = camera.brightness
                    second_call_count = camera.socket.send.call_count
                    assert second_call_count == first_call_count  # No new call

                    # Advance time beyond cache timeout (250ms > 200ms)
                    mock_time.return_value = 1000.25

                    # Third call after expiration - should trigger new inquiry
                    brightness3 = camera.brightness
                    third_call_count = camera.socket.send.call_count

                    # Should have made a new call
                    assert third_call_count > second_call_count

    def test_multiple_properties_independent_caching(self, camera):
        """Test that different properties have independent cache entries"""
        # Setup different mock responses for different commands
        responses = [
            bytes.fromhex("905000000a0bff"),  # brightness
            bytes.fromhex("90500002ff"),  # backlight (fixed hex)
            bytes.fromhex("90500000ff00ff"),  # zoom position (fixed hex)
        ]
        camera.socket.recv.side_effect = responses

        with patch("visca.interpret_inquire") as mock_interpret:
            mock_interpret.side_effect = [
                ["0a", "0b"],  # brightness
                [2],  # backlight
                ["0000", "ff00"],  # zoom
            ]

            # Call different properties
            brightness = camera.brightness
            backlight = camera.backlight
            zoom = camera.zoom_pos

            # Verify each triggered its own inquiry
            assert camera.socket.send.call_count == 3

            # Verify cache has entries for each
            cache_info = camera.get_cache_info()
            assert len(cache_info) == 3

            # Verify calling same properties again uses cache
            brightness2 = camera.brightness
            backlight2 = camera.backlight
            zoom2 = camera.zoom_pos

            # No additional calls should be made (still 3)
            assert camera.socket.send.call_count == 3

            # Results should be the same
            assert brightness == brightness2
            assert backlight == backlight2
            assert zoom == zoom2

    def test_setter_success_updates_cache(self, camera):
        """Test that successful setter operations update the cache"""
        with patch.object(camera, "run") as mock_run:
            mock_run.return_value = "Command Completed"

            # Set brightness value
            camera.brightness = 128

            # Verify run was called
            mock_run.assert_called_once()

            # Now get brightness - should return cached value without inquiry
            with patch.object(camera, "execute") as mock_execute:
                brightness = camera.brightness

                # Should not have called execute (used cached value)
                mock_execute.assert_not_called()

                # Should return the set value
                assert brightness == 128

    def test_setter_failure_clears_cache(self, camera):
        """Test that failed setter operations clear the cache for that property"""
        # First, populate cache with a brightness value
        camera.socket.recv.return_value = bytes.fromhex("905000000a0bff")
        with patch("visca.interpret_inquire") as mock_interpret:
            mock_interpret.return_value = ["0a", "0b"]

            # Get brightness to cache it
            initial_brightness = camera.brightness

            # Verify it's cached
            cache_info = camera.get_cache_info()
            assert len(cache_info) == 1

        # Now try to set brightness with a failing command
        with patch.object(camera, "run") as mock_run:
            mock_run.return_value = "Syntax Error"  # Failed command

            camera.brightness = 200

            # Cache should be cleared, so next inquiry should query camera again
            camera.socket.recv.return_value = bytes.fromhex("905000000c0dff")
            with patch("visca.interpret_inquire") as mock_interpret:
                mock_interpret.return_value = ["0c", "0d"]

                new_brightness = camera.brightness

                # Should have made a new inquiry (cache was cleared)
                assert new_brightness == ["0c", "0d"]

    def test_brightness_relative_uses_cached_current_value(self, camera):
        """Test that relative brightness change uses cached current value"""
        # Setup initial brightness in cache
        camera.socket.recv.return_value = bytes.fromhex("905000000a0bff")
        with patch("visca.interpret_inquire") as mock_interpret:
            mock_interpret.return_value = ["00", "50"]  # Brightness value 80 (0x50)

            # Get initial brightness to populate cache
            initial_brightness = camera.brightness

        # Reset mock to verify relative operation uses cache
        camera.socket.reset_mock()

        with patch.object(camera, "run") as mock_run:
            mock_run.return_value = "Command Completed"

            # Use relative brightness change
            new_brightness = camera.brightness_relative(20)  # 80 + 20 = 100

            # Should not have queried camera for current value (used cache)
            # Only the set operation should have been called
            camera.socket.send.assert_not_called()  # No inquiry was made
            mock_run.assert_called_once()  # Only the set command

            # Result should be 100 (80 + 20)
            assert new_brightness == 100

    def test_backlight_setter_cache_update_on_success(self, camera):
        """Test that backlight setter updates cache on successful operation"""
        with patch.object(camera, "run") as mock_run:
            mock_run.return_value = "Command Completed"

            # Set backlight
            camera.backlight = True

            # Now get backlight - should return cached value
            with patch.object(camera, "execute") as mock_execute:
                backlight_state = camera.backlight

                # Should not execute new inquiry (used cache)
                mock_execute.assert_not_called()

                # Should return the set value
                assert backlight_state == True

    def test_cache_info_provides_debugging_information(self, camera):
        """Test that cache info provides useful debugging information"""
        # Populate cache with some values
        camera.socket.recv.return_value = bytes.fromhex("905000000a0bff")
        with patch("visca.interpret_inquire") as mock_interpret:
            mock_interpret.return_value = ["0a", "0b"]

            # Mock time for testing age calculation
            with patch("time.time") as mock_time:
                mock_time.return_value = 1000.0
                brightness = camera.brightness

                mock_time.return_value = 1000.1  # 100ms later
                cache_info = camera.get_cache_info()

                assert len(cache_info) == 1

                # Should have the brightness command
                brightness_cmd = visca.commands["inq"]["brightness"]
                assert brightness_cmd in cache_info

                cache_entry = cache_info[brightness_cmd]
                assert cache_entry["value"] == ["0a", "0b"]
                assert abs(cache_entry["age_ms"] - 100.0) < 1.0  # Allow small tolerance
                assert cache_entry["expired"] == False  # Not expired yet

                # Test expired entry
                mock_time.return_value = 1000.25  # 250ms later
                cache_info = camera.get_cache_info()
                cache_entry = cache_info[brightness_cmd]
                assert abs(cache_entry["age_ms"] - 250.0) < 1.0  # Allow small tolerance
                assert cache_entry["expired"] == True  # Now expired

    def test_clear_cache_removes_all_entries(self, camera):
        """Test that clear_cache removes all cached entries"""
        # Populate cache with multiple values
        camera.socket.recv.return_value = bytes.fromhex("905000000a0bff")
        with patch("visca.interpret_inquire") as mock_interpret:
            mock_interpret.return_value = ["test"]

            # Add some cache entries
            camera.brightness
            camera.backlight
            camera.zoom_pos

            # Verify cache has entries
            cache_info = camera.get_cache_info()
            assert len(cache_info) > 0

            # Clear cache
            camera.clear_cache()

            # Verify cache is empty
            cache_info = camera.get_cache_info()
            assert len(cache_info) == 0

    def test_zoom_direct_success_updates_cache(self, camera):
        """Test that successful zoom direct operation updates cache"""
        with patch.object(camera, "run") as mock_run:
            mock_run.return_value = "Command Completed"

            # Call zoom direct
            camera.zoom("direct", 1000)

            # Cache should be updated, so inquiring zoom_pos should return cached value
            with patch.object(camera, "execute") as mock_execute:
                zoom_pos = camera.zoom_pos

                # Should not execute inquiry (used cached value from zoom operation)
                mock_execute.assert_not_called()

                # The implementation stores hex string values for zoom positions
                assert zoom_pos == "3e8"  # 1000 in decimal = 3e8 in hex

    def test_focus_direct_success_updates_cache(self, camera):
        """Test that successful focus direct operation updates cache"""
        with patch.object(camera, "run") as mock_run:
            mock_run.return_value = "Command Completed"

            # Call focus direct
            camera.focus("direct", 500)

            # Cache should be updated, so inquiring focus_pos should return cached value
            with patch.object(camera, "execute") as mock_execute:
                focus_pos = camera.focus_pos

                # Should not execute inquiry (used cached value from focus operation)
                mock_execute.assert_not_called()

                # The implementation stores hex string values for focus positions
                assert (
                    focus_pos == "01f4"
                )  # 500 in decimal = 1f4 in hex, padded to 4 chars

    def test_mixed_cache_behavior_with_time_progression(self, camera):
        """Test a complex scenario with mixed cache hits and misses over time"""
        camera.socket.recv.return_value = bytes.fromhex("905000000a0bff")

        with patch("visca.interpret_inquire") as mock_interpret:
            mock_interpret.return_value = ["test_value"]

            with patch("time.time") as mock_time:
                # Time 1000.0 - First brightness call (cache miss)
                mock_time.return_value = 1000.0
                brightness1 = camera.brightness
                first_call_count = camera.socket.send.call_count

                # Time 1000.1 - Second brightness call (cache hit)
                mock_time.return_value = 1000.1
                brightness2 = camera.brightness
                second_call_count = camera.socket.send.call_count
                assert second_call_count == first_call_count  # No new call

                # Time 1000.1 - Different property (cache miss)
                backlight = camera.backlight
                third_call_count = camera.socket.send.call_count
                assert third_call_count > second_call_count  # New call made

                # Time 1000.3 - First brightness call after expiration (cache miss)
                mock_time.return_value = 1000.3
                brightness3 = camera.brightness
                fourth_call_count = camera.socket.send.call_count
                assert fourth_call_count > third_call_count  # New call made

                # Time 1000.3 - Backlight still cached (cache hit)
                backlight2 = camera.backlight
                fifth_call_count = camera.socket.send.call_count
                assert fifth_call_count == fourth_call_count  # No new call


class TestCacheImplementationDetails:
    """Test implementation details of caching that ensure robustness"""

    @pytest.fixture
    def camera(self):
        """Create camera with minimal mocking for implementation tests"""
        with patch("socket.socket") as mock_socket_class:
            mock_socket = Mock()
            mock_socket.recv.return_value = bytes.fromhex("905000000a0bff")
            mock_socket_class.return_value = mock_socket
            cam = Camera()
            return cam

    def test_expired_entries_cleaned_up_on_access(self, camera):
        """Test that expired entries are removed when accessed"""
        with patch("visca.interpret_inquire") as mock_interpret:
            mock_interpret.return_value = ["test"]

            with patch("time.time") as mock_time:
                # Add entry at time 2000.0
                mock_time.return_value = 2000.0
                camera.brightness

                # Verify entry exists
                cache_info = camera.get_cache_info()
                assert len(cache_info) == 1

                # Access after expiration
                mock_time.return_value = 2000.3  # 300ms later
                camera.brightness  # This should clean up expired entry and add new one

                # Cache should still have 1 entry (old removed, new added)
                cache_info = camera.get_cache_info()
                assert len(cache_info) == 1

                # The entry should be fresh (not expired)
                for entry in cache_info.values():
                    assert not entry["expired"]
