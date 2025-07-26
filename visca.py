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

            key = key.replace("y", r"\w")
            regex = f"^{key}$"

            returns = []
            if re.match(regex, hex_return):
                returns.extend(
                    hex_return[digit[0] : digit[1]] for digit in result["data_digits"]
                )
                break
        return returns


class ViscaCommandBuilder:
    def __init__(self, camera_type):
        self.camera_type = importlib.import_module(f"cameras.{camera_type}")
        self.commands = self.camera_type.commands
        self.returns = self.camera_type.returns
        self.results = self.camera_type.results

    def build_command(self, command_name, *args, **kwargs):
        command = self.commands[command_name]
        command_str = command["command"]
        params = command["parameters"]
        real_params = []
        param_index = 0
        if len(args) + len(kwargs) != len(params):
            raise ValueError(
                f"Command {command_name} requires {len(params)} parameters, but {len(args)} were provided."
            )
        for param in params:
            # Pad the value to the required total length
            total_length = (
                param["length"] * param["splits"]
                if "splits" in param
                else param["length"]
            )
            if param["name"] in kwargs:
                value = kwargs[param["name"]]
            else:
                value = args[param_index]
                param_index += 1
            if value < param["min"] or value > param["max"]:
                raise ValueError(
                    f"Value {value} is out of range for {param['name']}. Range: {param['min']}-{param['max']}"
                )
            if param["type"] == "int":
                value = hex(value).lstrip("0x")
            value = "0" * (total_length - len(value)) + value
            if "splits" in param:
                # Split the value into chunks of param["length"]
                for i in range(param["splits"]):
                    start_idx = i * param["length"]
                    end_idx = start_idx + param["length"]
                    chunk = value[start_idx:end_idx]
                    real_params.append(chunk)
            else:
                real_params.append(value)
        for i, param in enumerate(real_params):
            if "p" not in command_str:
                warn(
                    f"Command {command_name} does not contain all provided parameters. Extra parameters: {real_params[i:]}",
                    ViscaException,
                )
            command_str = command_str.replace("p", param, 1)
        if "p" in command_str:
            warn(
                f"Command {command_name} not provided enough parameters. Missing parameters: {command_str.count('p')}",
                ViscaException,
            )
        return command_str
