import dataclasses
import hashlib
import logging
from functools import reduce
from typing import List, Optional


_LOGGER = logging.getLogger('devices')


@dataclasses.dataclass
class Device:
    component: str
    name: str
    key: str
    commands: dict
    manufacturer_info: dict
    discovery_payload: dict
    discovery_topic: str
    state_packet: str
    state_position: int


    def get_checksum(self, packet: bytearray):
        return '%02X' % reduce(lambda x, y: x + y, packet, 0)

    def get_hex_command(self, action):
        return []

    def get_state_topic(self, chunk: List[str]):
        return f"{self.component}/state"

    def get_state_key(self, chunk: List[str]):
        return 'state'

    def parse_state(self, packet: str):
        return None

    def get_ack(self, action: str):
        return self.commands.get(f'cmd_{action}_ack', None)

    def __init__(self, component, device_info, topic):
        self.component = component
        self.name = device_info['name']
        self.state_packet = device_info['state_packet']
        self.state_position = device_info['state_position']
        self.key = hashlib.md5(f"{self.component}-{self.name}".encode('utf-8')).hexdigest()
        self.commands = device_info['commands']
        self.discovery_topic = f'homeassistant/{self.component}/{topic}/{self.key}/config'
        self.manufacturer_info = {
            "manufacturer": "제일풍경채",
            "model": "CSH-5100",
            "name": "CVNET 월패드",
            "ids": "cvnet smart wallpad",
            "sw_version": "0.1"
        }
