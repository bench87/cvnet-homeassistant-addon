import dataclasses
import logging
from typing import List, Optional

from wallpad.devices.device import Device

_LOGGER = logging.getLogger('models')


@dataclasses.dataclass
class Mqtt:
    host: str = ""
    port: int = 1883
    user: str = ""
    password: str = ""
    topic: str = ""
    subscribe_command_topic: str = ""

    def __init__(self, mqtt_config):
        self.host = mqtt_config['host']
        self.port = mqtt_config['port']
        self.user = mqtt_config.get('user', '')
        self.password = mqtt_config.get('password', '')
        self.topic = mqtt_config['topic']
        self.subscribe_command_topic = f"{self.topic}/command/#"


@dataclasses.dataclass
class EW11:
    host: str = ''
    port: int = 8899

    def __init__(self, ew11_config):
        self.host = ew11_config['host']
        self.port = ew11_config['port']

@dataclasses.dataclass
class State:
    component: str
    state: dict
    state_topic: str

@dataclasses.dataclass
class Command:
    device: Device
    commands: List[str]
    action: str
    state: List[State] = None
    ack: Optional[str] = None


