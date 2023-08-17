import asyncio
import dataclasses
import logging.config
import importlib
from typing import List
from asyncio import Queue

from wallpad.models import Mqtt, EW11, Device

_LOGGER = logging.getLogger('root')


def create_instance(component, device, topic):
    try:
        module = importlib.import_module(f'wallpad.devices.{component}')
        component_class = getattr(module, component.capitalize())
        if component_class:
            return component_class(component, device, topic)
        else:
            _LOGGER.error(f"Unsupported component: {component}")
            raise ValueError(f"Unsupported component: {component}")
    except Exception as e:
        _LOGGER.error(f"{e.args}")
        raise e


@dataclasses.dataclass(slots=True)
class RuntimeConfig:
    debug: bool = False
    raw_configuration: dict = dataclasses.field(default_factory=dict)
    mqtt: Mqtt = None
    ew11: EW11 = None
    devices: List[Device] = None
    command_queue: Queue = None
    state_queue: Queue = None
    acks: dict = None

    def __init__(self, raw_config):
        self.mqtt = Mqtt(raw_config['mqtt'])
        self.ew11 = EW11(raw_config['ew11'])
        self.command_queue = asyncio.Queue()
        self.state_queue = asyncio.Queue()
        _devices = raw_config['devices'].items()
        self.devices = [create_instance(c, dev, self.mqtt.topic) for c, devs in _devices for dev in devs]

    def collect_ack(self):
        result = {}
        for item in self.devices:
            try:
                for k, v in item.commands.items():
                    if '_ack' in k:
                        result[v] = True
            except:
                pass
        return result

    def find_device_by_key(self, chunk: List[str]) -> Device:
        try:
            return [v for v in self.devices if v.key == chunk[-3]][0]
        except:
            msg = f'device key {chunk[-3]} not found'
            _LOGGER.error(msg)
            raise Exception(msg)
