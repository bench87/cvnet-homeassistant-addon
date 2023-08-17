import logging.config
import asyncio
import re

from wallpad.config import RuntimeConfig
from wallpad.models import Command

_LOGGER = logging.getLogger('ew11')
ACK = {}
received_packets = {}


async def command_consumer(writer, config: RuntimeConfig):
    while True:
        msg: Command = await config.command_queue.get()
        _LOGGER.debug(f"Consumed from queue: {msg}")
        retry_count = 5 if msg.ack else 2
        for cmd in msg.commands:
            for i in range(retry_count):
                await config.state_queue.put(msg.state)
                writer.write(bytes.fromhex(cmd))
                if not msg.ack:
                    _LOGGER.info(f'try write command {i} {cmd} no ack')
                    await asyncio.sleep(1)
                    break
                elif msg.ack not in ACK:
                    _LOGGER.info(f'try write command {i} {cmd}')
                    await asyncio.sleep(2)
                else:
                    _LOGGER.error('found ack')
                    del ACK[msg.ack]
                    break
        await writer.drain()
        config.command_queue.task_done()


async def state_parser(packet, config: RuntimeConfig):
    for dev in config.devices:
        state = dev.parse_state(packet)
        if state:
            await config.state_queue.put(state)


async def ew11_client(config: RuntimeConfig):
    regex_c = re.compile(r'(F7 .*? AA)')
    acks = config.collect_ack()
    while True:
        try:
            reader, writer = await asyncio.open_connection(config.ew11.host, config.ew11.port)
            _LOGGER.info('connected ew11')
            asyncio.ensure_future(asyncio.create_task(command_consumer(writer, config)))
            while True:
                data = await reader.read(512)
                packet = data.hex(' ').upper()
                # _LOGGER.info(packet)
                for p in regex_c.findall(packet):
                    # if '20 01 71 81' in p:
                    #     _LOGGER.error(p)

                    if p not in received_packets:
                        _LOGGER.info(p)
                    received_packets[p] = True

                    if p in acks:
                        _LOGGER.info(f"received ack {p}")
                        ACK[p] = True
                    await state_parser(p, config)
        except Exception as e:
            _LOGGER.error("socket connection lost %s" % e.args)
            await asyncio.sleep(5)
