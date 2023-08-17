import dataclasses
from typing import List, Optional

from wallpad.devices.device import Device, _LOGGER
from wallpad.models import State


@dataclasses.dataclass
class Climate(Device):

    mode: str = None
    set_temp: int = None
    curr_temp: int = None
    temp_checksum: int = None

    def get_action_keyword(self, chunks):
        action = chunks[-2]
        if action not in ['mode', 'temp', 'curr_temp']:
            raise ValueError(f'{action} is not support')
        return action

    def get_state_topic(self, chunk: List[str]):
        return self.discovery_payload[f'{self.get_action_keyword(chunk)}_stat_t']

    def get_state_key(self, chunk: List[str]):
        return f'{self.component}_{self.get_action_keyword(chunk)}'

    def get_ack(self, action: str):
        k = f'cmd_{action}_ack'
        if k not in self.commands:
            return self.commands['cmd_temp_ack']
        else:
            return self.commands.get(f'cmd_{action}_ack', None)

    def temp_hex(self, temp: int):
        packets = self.commands['cmd_heat'][0].split(' ')
        t = temp + 128
        new_temp = packets[1:5] + ['%02X' % t] + packets[6:-2]
        result = ' '.join(['F7'] + new_temp + ['%02X' % (t - self.temp_checksum), 'AA'])
        return result

    def get_hex_command(self, action):
        k = f'cmd_{action}'
        if k in self.commands:
            return self.commands['cmd_%s' % action]
        else:
            return [self.temp_hex(int(float(action)))]

    def parse_state(self, packet: str) -> Optional[List[State]]:
        packets = packet.split(' ')
        if self.state_packet in packet:
            set_temp = int(packets[self.state_position], 16) - 128
            if set_temp < 0:
                mode = 'off'
                set_temp = int(packets[self.state_position], 16)
            else:
                mode = 'heat'
            curr_temp = int(packets[self.state_position+1], 16)
            # if self.mode != mode or self.curr_temp != curr_temp or self.set_temp != set_temp:
            states = [State(self.component, {f'{self.component}_mode': mode}, self.discovery_payload['mode_stat_t']),
                      State(self.component, {f'{self.component}_curr_temp': curr_temp}, self.discovery_payload['curr_temp_t']),
                      State(self.component, {f'{self.component}_temp': set_temp}, self.discovery_payload['temp_stat_t']),
                      ]
            self.mode = mode
            self.set_temp = set_temp
            self.curr_temp = curr_temp
            _LOGGER.debug(f'{self.name} 모드: {mode} 설정 온도: {set_temp} 현재 온도: {curr_temp}')
            return states
        return None

    def __init__(self, component, device_info, topic):
        super().__init__(component, device_info, topic)
        self.temp_checksum = self.commands['temp_checksum']
        self.discovery_payload = {

            'name': self.name,
            "mode_cmd_t": f"{topic}/command/{component}/{self.key}/mode/set",
            "mode_stat_t": f"{topic}/{component}/{self.key}/mode/state",
            'mode_stat_tpl': "{{ value_json.%s }}" % f"{component}_mode",

            "temp_cmd_t": f"{topic}/command/{component}/{self.key}/temp/set",
            "temp_stat_t": f"{topic}/{component}/{self.key}/temp/state",
            'temp_stat_tpl': "{{ value_json.%s }}" % f"{component}_temp",

            "curr_temp_t": f"{topic}/{component}/{self.key}/curr_temp/state",
            'curr_temp_tpl': "{{ value_json.%s }}" % f"{component}_curr_temp",
            'modes': ['off', 'heat'],
            'min_temp': 18,
            'max_temp': 30,
            'ret': 'false',
            'qos': 0,
            "unique_id": f"{self.key}",
            "device": self.manufacturer_info
        }
