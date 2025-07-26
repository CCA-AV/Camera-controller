import visca
import socket
import time
from time import sleep


class Camera:
    def __init__(self, ip="192.168.0.25", port=1259, camera_type="ptzoptics"):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)

        self.parser = visca.ViscaParser(camera_type)
        self.builder = visca.ViscaCommandBuilder(camera_type)
        self.build_command = self.builder.build_command

        self.ip = ip
        self.port = port
        self.socket.connect((ip, port))
        self.commands = self.parser.commands

        # Initialize cache system
        self._cache = {}
        self._cache_timeout = 0.2  # 200ms timeout

    def _get_cached_value(self, command):
        """Get cached value if unexpired, otherwise return None"""
        if command in self._cache:
            value, timestamp = self._cache[command]
            if time.time() - timestamp < self._cache_timeout:
                return value
            else:
                # Remove expired cache entry
                del self._cache[command]
        return None

    def _update_cache(self, command, value):
        """Update cache with new value and current timestamp"""
        self._cache[command] = (value, time.time())

    def _clear_cache_for_property(self, property_name):
        """Clear cache entries related to a specific property"""
        # Map property names to their corresponding inquiry commands
        property_command_map = {
            "backlight": self.commands["inq"]["backlight_mode"],
            "power": self.commands["inq"]["other_block"],
        }

        if property_name in property_command_map:
            command = property_command_map[property_name]
        elif property_name in self.commands["inq"]:
            command = self.commands["inq"][property_name]
        else:
            command = None

        if command in self._cache and command is not None:
            del self._cache[command]

    def get_cache_info(self):
        """Get information about current cache state for debugging
        cache_info[command] = {
            "value": value,
            "age_ms": age * 1000,
            "expired": expired,
        }
        """

        current_time = time.time()
        cache_info = {}

        for command, (value, timestamp) in self._cache.items():
            age = current_time - timestamp
            expired = age >= self._cache_timeout
            cache_info[command] = {
                "value": value,
                "age_ms": age * 1000,
                "expired": expired,
            }

        return cache_info

    def clear_cache(self):
        """Clear all cached values"""
        self._cache.clear()

    def close(self):
        self.socket.close()

    def execute(self, command):
        data = bytes.fromhex(command)
        self.socket.send(data)

        return self.socket.recv(256).hex()

    def check(self):
        data = bytes.fromhex("")
        self.socket.send(data)

        return self.socket.recv(256).hex()

    def run(self, command):
        result = self.execute(command)
        print(result, self.parser.interpret_completion(result))
        while self.parser.interpret_completion(result) == "Command Accepted":
            result = self.check()
            print("r", result, self.parser.interpret_completion(result))
        return self.parser.interpret_completion(result)

    def inquire(self, command):
        # First check cache for unexpired value
        cached_value = self._get_cached_value(command)
        if cached_value is not None:
            return cached_value

        # Cache miss or expired - execute the command
        result = self.execute(command)
        # print(result, command)
        interpreted_result = self.parser.interpret_inquire(result)

        # Update cache with new value
        self._update_cache(command, interpreted_result)

        return interpreted_result

    @property
    def brightness(self):
        return self.inquire(self.commands["inq"]["brightness"])

    @brightness.setter
    def brightness(self, value):
        """Set brightness directly. Value should be an integer (0-255 range typically)"""

        command = self.build_command("brightness_direct", value)
        result = self.run(command)

        # If command was successful, update cache
        if result == "Command Completed":
            # Update cache with the new value
            self._update_cache(self.commands["inq"]["brightness"], value)
        else:
            # If command failed, clear the cache for this property
            self._clear_cache_for_property("brightness")

    def property_relative(self, property_name, delta):
        """Change brightness by a relative amount. Delta can be positive or negative."""
        # Get current brightness (uses cache if available)
        current_state = getattr(self, property_name)

        # Parse current brightness from inquiry result
        # The inquiry returns a list like ['00', '0a'] for brightness position
        if isinstance(current_state, list):
            current_val = int("".join(current_state), 16)
        elif isinstance(current_state, str):
            current_val = int(current_state, 16)
        else:
            current_val = current_state

        new_val = current_val + delta

        # Set new brightness value (this will update cache if successful)
        setattr(self, property_name, new_val)

        return new_val

    @property
    def backlight(self):
        return self.inquire(self.commands["inq"]["backlight_mode"])

    @backlight.setter
    def backlight(self, value):
        command = self.build_command("backlight", backlight=2 if value else 3)
        result = self.run(command)

        # If command was successful, update cache
        if result == "Command Completed":
            # Update cache with the new value
            self._update_cache(self.commands["inq"]["backlight_mode"], value)
        else:
            # If command failed, clear the cache for this property
            self._clear_cache_for_property("backlight")

    @property
    def power(self):
        return self.inquire(self.commands["inq"]["other_block"])

    @power.setter
    def power(self, state):
        if state:
            self.on()
        else:
            self.off()

    @property
    def zoom_pos(self):
        return self.inquire(self.commands["inq"]["zoom_pos"])

    @zoom_pos.setter
    def zoom_pos(self, value):
        # First, clear cache for this property
        self._clear_cache_for_property("zoom_pos")
        self.zoom("direct", value)
        # Note: zoom method will handle cache update based on its success

    @property
    def focus_pos(self):
        return self.inquire(self.commands["inq"]["focus_pos"])

    @focus_pos.setter
    def focus_pos(self, value):
        # First, clear cache for this property
        self._clear_cache_for_property("focus_pos")
        self.focus("direct", value)
        # Note: focus method will handle cache update based on its success

    def off(self):
        self.run(self.commands["power_off"])

    def on(self):
        self.run(self.commands["power_on"])

    def restart(self):
        self.off()
        while self.power == False:
            pass
        # repeat while other_block_inq_0 = 1
        self.on()

    def zoom(self, _type="direct", val=-1):
        """
        zoom(type, value)

        type = "direct":
            MIN: 0
            MAX: 4 000 000  [HEX]
                    OR
                 67 108 864 [DEC]

        type = "tele" or "wide":
            MIN: 0
            MAX: 7
        """
        if _type in ["tele", "wide"]:
            if val == -1:
                command = self.build_command(f"zoom_{_type}_std")
            else:
                command = self.build_command(f"zoom_{_type}_var", val)
        elif _type == "direct":
            command = self.build_command("zoom_direct", val)

        result = self.run(command)

        # If zoom direct command was successful, update cache
        if result == "Command Completed" and _type == "direct":
            self._update_cache(self.commands["inq"]["zoom_pos"], val)

    def focus(self, _type="direct", val=-1):
        """
        zoom(type, value)

        type = "direct":
            MIN: 0
            MAX: 6EA  [HEX]
                    OR
                 1770 [DEC]

        type = "far" or "near":
            MIN: 0
            MAX: 7
        """
        if _type in ["far", "near"]:
            if val == -1:
                command = self.build_command(f"focus_{_type}_std")
            else:
                command = self.build_command(f"focus_{_type}_var", val)
        elif _type == "direct":
            command = self.build_command("focus_direct", val)

        result = self.run(command)

        # If focus direct command was successful, update cache
        if result == "Command Completed" and _type == "direct":
            self._update_cache(self.commands["inq"]["focus_pos"], val)
        if result == "Command Completed" and _type == "direct":
            self._update_cache(self.commands["inq"]["focus_pos"], val)


if __name__ == "__main__":
    cam = Camera()
    # cam.off()

    # cam.on()

    print(cam.power)
    print("fp,", cam.focus_pos)
    cam.zoom_pos = "2080309"
    print("xp,", cam.zoom_pos)
    print("fp,", cam.focus_pos)
    cam.focus_pos = 850
    print("fp,", cam.focus_pos)
