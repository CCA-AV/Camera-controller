import visca
import socket
import time
from time import sleep


class Camera:
    def __init__(self, ip="192.168.0.25", port=1259):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)

        self.ip = ip
        self.port = port
        self.socket.connect((ip, port))
        self.commands = visca.commands

        self._cache = {}
        self._cache_timeout = 0.2

    def _get_cached_value(self, command):
        return None

    def get_cache_info(self):
        """Get information about current cache state for debugging
        cache_info[command] = {
            "value": value,
            "age_ms": age * 1000,
            "expired": expired,
        }
        """
        pass

    def clear_cache(self):
        pass

    def close(self):
        self.socket.close()

    def execute(self, command):
        data = bytes.fromhex(command)
        self.socket.send(data)

        back = self.socket.recv(256).hex()
        return back

    def check(self):
        data = bytes.fromhex("")
        self.socket.send(data)

        back = self.socket.recv(256).hex()
        return back

    def run(self, command):
        result = self.execute(command)
        print(result, visca.interpret_completion(result))
        while visca.interpret_completion(result) == "Command Accepted":
            result = self.check()
            print("r", result, visca.interpret_completion(result))
        return visca.interpret_completion(result)

    def inquire(self, command):
        result = self.execute(command)
        # print(result, command)
        return visca.interpret_inquire(result)

    @property
    def brightness(self):
        return self.inquire(self.commands["inq"]["brightness"])

    @brightness.setter
    def brightness(self, value):
        """Set brightness directly. Value should be a hex value or integer (0-255 range typically)"""
        if type(value) == int:
            # Convert to hex format expected by camera (2 hex digits)
            hex_val = hex(value).lstrip("0x").upper()
            hex_val = "0" * (2 - len(hex_val)) + hex_val
            p_val = hex_val[0]
            q_val = hex_val[1]
        else:
            # Assume hex string, take first 2 characters
            hex_val = str(value).lstrip("0x").upper()
            hex_val = "0" * (2 - len(hex_val)) + hex_val
            p_val = hex_val[0]
            q_val = hex_val[1]

        command = (
            self.commands["brightness_direct"].replace("P", p_val).replace("Q", q_val)
        )
        result = self.run(command)

    @property
    def backlight(self):
        return self.inquire(self.commands["inq"]["backlight_mode"])

    @backlight.setter
    def backlight(self, value):
        command = self.commands["backlight"]
        command = command.replace("P", "2" if value else "3")
        result = self.run(command)

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
        self.zoom("direct", value)

    @property
    def focus_pos(self):
        return self.inquire(self.commands["inq"]["focus_pos"])

    @focus_pos.setter
    def focus_pos(self, value):
        self.focus("direct", value)

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
        if _type == "tele" or _type == "wide":
            if val == -1:
                command = self.commands["zoom_" + _type + "_std"]
            else:
                command = self.commands["zoom_" + _type + "_var"].replace("p", str(val))
        elif _type == "direct":
            if type(val) == int:
                val = str(hex(val)).lstrip("0x")
            else:
                val = str(val.lstrip("0x"))
            print(val, "0" * (8 - len(val)) + val)
            command = self.commands["zoom_direct"].replace(
                "p", "0" * (8 - len(val)) + val
            )

        self.run(command)

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
        if _type == "far" or _type == "near":
            if val == -1:
                command = self.commands["focus_" + _type + "_std"]
            else:
                command = self.commands["focus_" + _type + "_var"].replace(
                    "p", str(val)
                )
        elif _type == "direct":
            if type(val) == int:
                val = str(hex(val)).lstrip("0x")
            else:
                val = str(val.lstrip("0x"))
                if len(val) > 4:
                    val = val[0] + val[2] + val[4]
            val = "0" * (4 - len(val)) + val
            command = (
                self.commands["focus_direct"]
                .replace("p", val[0])
                .replace("q", val[1])
                .replace("r", val[2])
                .replace("s", val[3])
            )
        print(command)
        self.run(command)


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
