import yaml
import logging
import logging.config
import sys
import os
import asyncio
from wallpad.config import RuntimeConfig
from wallpad.ew11_client import ew11_client
from wallpad.mqtt_client import mqtt_listener
from collections import defaultdict


_LOGGER = logging.getLogger('ew11')
ACK = {}
STATE = defaultdict(dict)
received_packets = {}


async def main() -> int:
    config_dir = os.path.abspath(os.path.join(os.getcwd(), 'wallpad/config'))
    with open(os.path.join(config_dir, 'configurations.yml')) as f:
        client_config = yaml.load(f, Loader=yaml.FullLoader)
        if os.environ.get("MQTT_USER") and os.environ.get("MQTT_PASSWORD"):
            client_config['mqtt']['user'] = os.environ.get("MQTT_USER")
            client_config['mqtt']['password'] = os.environ.get("MQTT_PASSWORD")

    logging.config.dictConfig(client_config['logging'])
    _LOGGER.info("Config directory: %s" % config_dir)

    runtimeConfig = RuntimeConfig(client_config)
    await asyncio.gather(asyncio.create_task(ew11_client(runtimeConfig)),
                         asyncio.create_task(mqtt_listener(runtimeConfig)))


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
