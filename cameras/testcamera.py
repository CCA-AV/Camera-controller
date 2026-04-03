import copy

from cameras import ptzoptics
from cameras.testcamera_sim import SimulatedViscaSocket


commands = copy.deepcopy(ptzoptics.commands)
returns = copy.deepcopy(ptzoptics.returns)
results = copy.deepcopy(ptzoptics.results)


def connect(ip, port):
    return SimulatedViscaSocket(ip, port)
