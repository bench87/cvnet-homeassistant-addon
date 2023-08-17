import dataclasses
from typing import Optional, List

from wallpad.devices.device import Device, _LOGGER
from wallpad.models import State


@dataclasses.dataclass
class Switch(Device):
    current_state: str = None

    def conv_onoff(self, p):
        if p == '01':
            return 'ON'
        elif p == '00':
            return 'OFF'
        else:
            raise Exception(f"can not convert onoff {p}")

    def get_hex_command(self, action):
        return self.commands['cmd_%s' % action]

    def parse_state(self, packet: str) -> Optional[List[State]]:
        packets = packet.split(' ')
        if self.state_packet in packet:
            received_state = self.conv_onoff(packets[self.state_position])
            _LOGGER.debug(f'{self.component} {self.name} {self.current_state}')
            if self.current_state != received_state:
                self.current_state = received_state
                _LOGGER.info(f'{self.component} {self.name} {self.current_state}')
                state = State(self.component, {'state': self.current_state}, self.discovery_payload['stat_t'])
                return [state]

        return None

    def __init__(self, component, device_info, topic: str):
        super().__init__(component, device_info, topic)
        self.discovery_payload = {
            "cmd_t": f"{topic}/command/{component}/{self.key}/cmd/set",
            "device": self.manufacturer_info,
            "name": self.name,
            "stat_t": f"{topic}/{component}/{self.key}/state",
            "unique_id": f"{self.key}",
            "value_template": "{{ value_json.state }}"
        }
