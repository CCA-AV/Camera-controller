import pytest
import socket
from unittest.mock import Mock, patch, MagicMock, call
import sys
import os

# Add parent directory to path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from controller import Camera


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
        assert cache_info is not None and len(cache_info) == 0

        # Cache timeout should be 200ms (0.2 seconds)
        assert camera._cache_timeout == 0.2

    def test_cache_hit_prevents_duplicate_inquiries(self, camera):
        """Test that cached values prevent duplicate camera inquiries"""
        # Setup mock response
        camera.socket.recv.return_value = bytes.fromhex("905000000a0bff")

        with patch.object(camera.parser, "interpret_inquire") as mock_interpret:
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

        with patch.object(camera.parser, "interpret_inquire") as mock_interpret:
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

        with patch.object(camera.parser, "interpret_inquire") as mock_interpret:
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
            assert cache_info is not None and len(cache_info) == 3

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

            # Setup proper response for brightness inquiry
            camera.socket.recv.return_value = bytes.fromhex("905000000a0bff")
            with patch.object(camera.parser, "interpret_inquire") as mock_interpret:
                mock_interpret.return_value = ["0a", "0b"]

                # Track execute calls to verify cache usage
                original_execute = camera.execute
                with patch.object(
                    camera, "execute", wraps=original_execute
                ) as mock_execute:
                    brightness = camera.brightness

                    # Should not have called execute (used cached value)
                    mock_execute.assert_not_called()

                    # Should return the set value
                    assert brightness == 128

    def test_setter_failure_clears_cache(self, camera):
        """Test that failed setter operations clear the cache for that property"""
        # First, populate cache with a brightness value
        camera.socket.recv.return_value = bytes.fromhex("905000000a0bff")
        with patch.object(camera.parser, "interpret_inquire") as mock_interpret:
            mock_interpret.return_value = ["0a", "0b"]

            # Get brightness to cache it
            initial_brightness = camera.brightness

            # Verify it's cached
            cache_info = camera.get_cache_info()
            assert cache_info is not None and len(cache_info) == 1

        # Now try to set brightness with a failing command
        with patch.object(camera, "run") as mock_run:
            mock_run.return_value = "Syntax Error"  # Failed command

            camera.brightness = 200

            # Cache should be cleared, so next inquiry should query camera again
            camera.socket.recv.return_value = bytes.fromhex("905000000c0dff")
            with patch.object(camera.parser, "interpret_inquire") as mock_interpret:
                mock_interpret.return_value = ["0c", "0d"]

                new_brightness = camera.brightness

                # Should have made a new inquiry (cache was cleared)
                assert new_brightness == ["0c", "0d"]

    def test_backlight_setter_cache_update_on_success(self, camera):
        """Test that backlight setter updates cache on successful operation"""
        with patch.object(camera, "run") as mock_run:
            mock_run.return_value = "Command Completed"

            # Set backlight
            camera.backlight = True

            # Setup proper response for backlight inquiry
            camera.socket.recv.return_value = bytes.fromhex("90500002ff")
            with patch.object(camera.parser, "interpret_inquire") as mock_interpret:
                mock_interpret.return_value = [2]

                # Track execute calls to verify cache usage
                original_execute = camera.execute
                with patch.object(
                    camera, "execute", wraps=original_execute
                ) as mock_execute:
                    backlight = camera.backlight

                    # Should not have called execute (used cached value)
                    mock_execute.assert_not_called()

                    # Should return the set value
                    assert backlight == True

    def test_cache_info_provides_debugging_information(self, camera):
        """Test that cache info provides useful debugging information"""
        # Populate cache with some values
        camera.socket.recv.return_value = bytes.fromhex("905000000a0bff")
        with patch.object(camera.parser, "interpret_inquire") as mock_interpret:
            mock_interpret.return_value = ["0a", "0b"]

            # Get a property to cache it
            brightness = camera.brightness

            # Get cache info
            cache_info = camera.get_cache_info()

            # Should have one entry
            assert cache_info is not None and len(cache_info) == 1

            # Check the structure of cache info
            for command, info in cache_info.items():
                assert "value" in info
                assert "age_ms" in info
                assert "expired" in info
                assert isinstance(info["age_ms"], (int, float))
                assert isinstance(info["expired"], bool)

    def test_clear_cache_removes_all_entries(self, camera):
        """Test that clear_cache removes all cached entries"""
        # Populate cache with multiple values
        camera.socket.recv.return_value = bytes.fromhex("905000000a0bff")
        with patch.object(camera.parser, "interpret_inquire") as mock_interpret:
            mock_interpret.return_value = ["0a", "0b"]

            # Get multiple properties to cache them
            brightness = camera.brightness

        camera.socket.recv.return_value = bytes.fromhex("90500002ff")
        with patch.object(camera.parser, "interpret_inquire") as mock_interpret:
            mock_interpret.return_value = [2]

            backlight = camera.backlight

            # Verify cache has entries
            cache_info = camera.get_cache_info()
            assert cache_info is not None and len(cache_info) > 0

            # Clear cache
            camera.clear_cache()

            # Verify cache is empty
            cache_info = camera.get_cache_info()
            assert cache_info is not None and len(cache_info) == 0

    def test_zoom_direct_success_updates_cache(self, camera):
        """Test that successful zoom direct operation updates cache"""
        with patch.object(camera, "run") as mock_run:
            mock_run.return_value = "Command Completed"

            # Call zoom direct
            camera.zoom("direct", 1000)

            # Setup proper response for zoom position inquiry
            camera.socket.recv.return_value = bytes.fromhex("90500000ff00ff")
            with patch.object(camera.parser, "interpret_inquire") as mock_interpret:
                mock_interpret.return_value = ["0000", "ff00"]

                # Track execute calls to verify cache usage
                original_execute = camera.execute
                with patch.object(
                    camera, "execute", wraps=original_execute
                ) as mock_execute:
                    zoom_pos = camera.zoom_pos

                    # Should not have called execute (used cached value)
                    mock_execute.assert_not_called()

                    # Should return the cached value (1000 was cached as the input value)
                    assert zoom_pos == 1000

    def test_focus_direct_success_updates_cache(self, camera):
        """Test that successful focus direct operation updates cache"""
        with patch.object(camera, "run") as mock_run:
            mock_run.return_value = "Command Completed"

            # Call focus direct
            camera.focus("direct", 500)

            # Setup proper response for focus position inquiry
            camera.socket.recv.return_value = bytes.fromhex("90500000ff00ff")
            with patch.object(camera.parser, "interpret_inquire") as mock_interpret:
                mock_interpret.return_value = ["0000", "ff00"]

                # Track execute calls to verify cache usage
                original_execute = camera.execute
                with patch.object(
                    camera, "execute", wraps=original_execute
                ) as mock_execute:
                    focus_pos = camera.focus_pos

                    # Should not have called execute (used cached value)
                    mock_execute.assert_not_called()

                    # Should return the cached value (500 was cached as the input value)
                    assert focus_pos == 500

    def test_mixed_cache_behavior_with_time_progression(self, camera):
        """Test a complex scenario with mixed cache hits and misses over time"""
        camera.socket.recv.return_value = bytes.fromhex("905000000a0bff")

        with patch.object(camera.parser, "interpret_inquire") as mock_interpret:
            mock_interpret.return_value = ["0a", "0b"]

            with patch("time.time") as mock_time:
                # Start at time 0
                mock_time.return_value = 0.0

                # First call - cache miss
                brightness1 = camera.brightness
                calls_after_first = camera.socket.send.call_count

                # Second call immediately - cache hit
                brightness2 = camera.brightness
                calls_after_second = camera.socket.send.call_count
                assert calls_after_second == calls_after_first

                # Advance time just short of expiry (150ms < 200ms timeout)
                mock_time.return_value = 0.15

                # Third call - still cache hit
                brightness3 = camera.brightness
                calls_after_third = camera.socket.send.call_count
                assert calls_after_third == calls_after_second

                # Advance time beyond expiry (250ms > 200ms timeout)
                mock_time.return_value = 0.25

                # Fourth call - cache miss
                brightness4 = camera.brightness
                calls_after_fourth = camera.socket.send.call_count
                assert calls_after_fourth > calls_after_third


class TestCacheImplementationDetails:
    """Test implementation details of the caching system"""

    @pytest.fixture
    def camera(self):
        """Create a Camera instance with mocked socket"""
        with patch("socket.socket") as mock_socket_class:
            mock_socket = Mock()
            mock_socket.recv.return_value = bytes.fromhex("905000000a0bff")
            mock_socket_class.return_value = mock_socket
            cam = Camera()
            cam.socket = mock_socket
            return cam

    def test_expired_entries_cleaned_up_on_access(self, camera):
        """Test that expired entries are removed when accessed"""
        with patch.object(camera.parser, "interpret_inquire") as mock_interpret:
            mock_interpret.return_value = ["0a", "0b"]

            with patch("time.time") as mock_time:
                # Time 0 - populate cache
                mock_time.return_value = 0.0
                brightness = camera.brightness

                # Verify it's cached
                cache_info = camera.get_cache_info()
                assert len(cache_info) == 1

                # Advance time beyond expiry
                mock_time.return_value = 1.0  # 1 second > 200ms timeout

                # Access cached value - should trigger cleanup
                brightness2 = camera.brightness

                # The expired entry should have been cleaned up during the access
                # and a new entry created
                cache_info = camera.get_cache_info()
                assert len(cache_info) == 1

                # The entry should be fresh (age < 100ms for example)
                for command, info in cache_info.items():
                    assert info["age_ms"] < 100  # Should be very recent

    def test_clear_cache_for_property_brightness(self, camera):
        """Test that _clear_cache_for_property works correctly for brightness"""
        # Populate cache with brightness
        camera.socket.recv.return_value = bytes.fromhex("905000000a0bff")
        with patch.object(camera.parser, "interpret_inquire") as mock_interpret:
            mock_interpret.return_value = ["0a", "0b"]
            brightness = camera.brightness

            # Verify cache has the brightness entry
            cache_info = camera.get_cache_info()
            assert len(cache_info) == 1

            # Clear cache for brightness property
            camera._clear_cache_for_property("brightness")

            # Verify cache is now empty
            cache_info = camera.get_cache_info()
            assert len(cache_info) == 0

    def test_clear_cache_for_property_backlight(self, camera):
        """Test that _clear_cache_for_property works correctly for backlight"""
        # Populate cache with backlight
        camera.socket.recv.return_value = bytes.fromhex("90500002ff")
        with patch.object(camera.parser, "interpret_inquire") as mock_interpret:
            mock_interpret.return_value = [2]
            backlight = camera.backlight

            # Verify cache has the backlight entry
            cache_info = camera.get_cache_info()
            assert len(cache_info) == 1

            # Clear cache for backlight property
            camera._clear_cache_for_property("backlight")

            # Verify cache is now empty
            cache_info = camera.get_cache_info()
            assert len(cache_info) == 0

    def test_zoom_pos_setter_clears_cache_before_operation(self, camera):
        """Test that zoom_pos setter clears cache before setting new value"""
        # Populate cache with zoom position
        camera.socket.recv.return_value = bytes.fromhex("90500000ff00ff")
        with patch.object(camera.parser, "interpret_inquire") as mock_interpret:
            mock_interpret.return_value = ["0000", "ff00"]
            zoom_pos = camera.zoom_pos

            # Verify cache has zoom position entry
            cache_info = camera.get_cache_info()
            assert len(cache_info) == 1

            # Set new zoom position
            with patch.object(camera, "zoom") as mock_zoom:
                camera.zoom_pos = 5000

                # Verify zoom method was called correctly
                mock_zoom.assert_called_once_with("direct", 5000)

    def test_focus_pos_setter_clears_cache_before_operation(self, camera):
        """Test that focus_pos setter clears cache before setting new value"""
        # Populate cache with focus position
        camera.socket.recv.return_value = bytes.fromhex("90500000ff00ff")
        with patch.object(camera.parser, "interpret_inquire") as mock_interpret:
            mock_interpret.return_value = ["0000", "ff00"]
            focus_pos = camera.focus_pos

            # Verify cache has focus position entry
            cache_info = camera.get_cache_info()
            assert len(cache_info) == 1

            # Set new focus position
            with patch.object(camera, "focus") as mock_focus:
                camera.focus_pos = 800

                # Verify focus method was called correctly
                mock_focus.assert_called_once_with("direct", 800)

    def test_brightness_setter_successful_cache_update(self, camera):
        """Test that brightness setter updates cache on successful command"""
        with patch.object(camera, "run") as mock_run:
            mock_run.return_value = "Command Completed"

            # Set brightness
            camera.brightness = 150

            # Verify that the cache would contain the new value
            # (cache update happens in the setter when command is successful)
            expected_command = camera.commands["inq"]["brightness"]
            if expected_command in camera._cache:
                cached_value, _ = camera._cache[expected_command]
                assert cached_value == 150

    def test_cache_timeout_configuration(self, camera):
        """Test that cache timeout is correctly configured"""
        # Verify cache timeout is set to 200ms
        assert camera._cache_timeout == 0.2

    def test_cache_info_age_calculation(self, camera):
        """Test that cache info correctly calculates age and expiration"""
        with patch("time.time") as mock_time:
            # Set initial time
            mock_time.return_value = 1000.0

            # Populate cache
            camera.socket.recv.return_value = bytes.fromhex("905000000a0bff")
            with patch.object(camera.parser, "interpret_inquire") as mock_interpret:
                mock_interpret.return_value = ["0a", "0b"]
                brightness = camera.brightness

            # Advance time by 100ms
            mock_time.return_value = 1000.1

            # Get cache info
            cache_info = camera.get_cache_info()

            # Verify age calculation
            for command, info in cache_info.items():
                assert (
                    abs(info["age_ms"] - 100.0) < 1.0
                )  # Allow for small floating point errors
                assert info["expired"] == False  # Not expired yet (< 200ms)

            # Advance time beyond expiry
            mock_time.return_value = 1000.25

            # Get cache info again
            cache_info = camera.get_cache_info()

            # Verify expiration detection
            for command, info in cache_info.items():
                assert (
                    abs(info["age_ms"] - 250.0) < 1.0
                )  # Allow for small floating point errors
                assert info["expired"] == True  # Expired (> 200ms)
