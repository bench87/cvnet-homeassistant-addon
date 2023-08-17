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
                _LOGGER.info(f'Send the {cmd} on the {i + 1} attempt.')
                await asyncio.sleep(retry_count)
                if not msg.ack:
                    _LOGGER.info(f'No ACK is set, so it will be sent twice.')
                    await asyncio.sleep(retry_count)
                    break
                elif msg.ack not in ACK:
                    _LOGGER.info(f'After 2 sec, receive an ACK {msg.ack} or send the command up to 5 times.')
                else:
                    _LOGGER.error(f"it received an ACK {msg.ack}, so we don't retransmit.")
                    del ACK[msg.ack]
                    break
                await asyncio.sleep(2)
        await writer.drain()
        config.command_queue.task_done()


async def state_parser(packet, config: RuntimeConfig):
    for dev in config.devices:
        state = dev.parse_state(packet)
        if state:
            await config.state_queue.put(state)


async def ew11_client(config: RuntimeConfig):
    regex_c = re.compile(r'(F7 .*? AA)')
    while True:
        try:
            reader, writer = await asyncio.open_connection(config.ew11.host, config.ew11.port)
            _LOGGER.info('connected ew11')
            asyncio.ensure_future(asyncio.create_task(command_consumer(writer, config)))
            while True:
                data = await reader.read(15)
                packet = data.hex(' ').upper()
                # _LOGGER.info(packet)
                for p in regex_c.findall(packet):
                    if 'F7 20 01 21 9F' in p:
                        _LOGGER.error(p)

                    if p not in received_packets:
                        _LOGGER.info(p)
                    received_packets[p] = True

                    if p[:14] in config.acks:
                        _LOGGER.info(f"received an ack {p}")
                        ACK[p[:14]] = True
                    await state_parser(p, config)
        except Exception as e:
            _LOGGER.error("socket connection lost %s" % e.args)
            await asyncio.sleep(5)
