import dataclasses
from typing import Optional, List

from wallpad.devices.device import Device, _LOGGER
from wallpad.models import State


@dataclasses.dataclass
class Fan(Device):
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
            mode_dic = {'00': 'off', '01': 'low', '02': 'medium', '03': 'high'}
            power = 'on' if packets[5] == '01' else 'off'
            mode = mode_dic.get(packets[7])
            return [State(self.component, {'mode': mode}, self.discovery_payload['pr_mode_stat_t']),
                    State(self.component, {'state': power}, self.discovery_payload['stat_t'])]

        return None

    def __init__(self, component, device_info, topic: str):
        super().__init__(component, device_info, topic)

        self.discovery_payload = {
            "cmd_t": f"{topic}/command/{component}/{self.key}/cmd/set",
            "device": self.manufacturer_info,
            "name": self.name,
            "stat_t": f"{topic}/{component}/{self.key}/state",
            "stat_val_tpl": "{{ value_json.state }}",
            "pr_mode_stat_t": f"{topic}/{component}/{self.key}/state",
            "pr_mode_val_tpl": "{{ value_json.mode }}",
            "pr_mode_cmd_t": f"{topic}/command/{component}/{self.key}/mode/set",
            "pr_mode_cmd_tpl": '{{ value }}',
            "pr_modes": ['off', 'low', 'medium', 'high'],
            'pl_on': 'on',
            'pl_off': 'off',
            'qos': 0,
            "unique_id": f"{self.key}",
        }
