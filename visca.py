from warnings import warn
import importlib
import re


class ViscaException(Warning):
    pass


class ViscaParser:
    def __init__(self, camera_type):
        try:
            self.camera_type = importlib.import_module(f"cameras.{camera_type}")
            self.commands = self.camera_type.commands
            self.returns = self.camera_type.returns
            self.results = self.camera_type.results
        except Exception as e:
            warn(f"Failed to import camera type {camera_type}: {e}", ViscaException)
            raise e

    def interpret_completion(self, hex_return):
        hex_return = f"{hex_return[:3]}y{hex_return[4:]}"
        hex_return = hex_return.lower()
        if hex_return not in self.returns.keys():
            return None
        result = self.returns[hex_return]
        if result["status"] != 0:
            warn(result["text"], ViscaException)
        return result["text"]

    def interpret_inquire(self, hex_return):
        if result := self.interpret_completion(hex_return):
            return result
        hex_return = hex_return.lower()
        for key in self.results:
            result = self.results[key]

            key = key.replace("y", "\w")
            regex = f"^{key}$"

            returns = []
            if re.match(regex, hex_return):
                returns.extend(
                    hex_return[digit[0] : digit[1]] for digit in result["data_digits"]
                )
                break
        return returns
