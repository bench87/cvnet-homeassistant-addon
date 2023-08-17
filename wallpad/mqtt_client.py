import logging
import asyncio
from typing import List

import aiomqtt
import json


from wallpad.config import RuntimeConfig
from wallpad.models import Command, State
_LOGGER = logging.getLogger('mqtt')

async def device_discovery(client, devices):
    for item in devices:
        payload = json.dumps(item.discovery_payload, ensure_ascii=False, indent=2)
        _LOGGER.info(f'discovery {item.component} {item.name}')
        _LOGGER.debug(f"discovery topic => {item.discovery_topic} payload => {payload}")
        await client.publish(item.discovery_topic, payload=payload)


async def state_q_consumer(client,  config: RuntimeConfig):
    while True:
        message: List[State] = await config.state_queue.get()
        if isinstance(message, State):
            _LOGGER.error('The message must be of type List[State]')
            message = [message]
        for msg in message:
            _LOGGER.debug(f"consumed from state queue: {msg}")
            await client.publish(f'{msg.state_topic}', payload=json.dumps(msg.state))
        config.state_queue.task_done()


async def command_consumer(client, config: RuntimeConfig):

    async with client.messages() as messages:
        _LOGGER.info(f"mqtt subscribe topic {config.mqtt.subscribe_command_topic}/#")
        await client.subscribe(config.mqtt.subscribe_command_topic)
        async for message in messages:
            payload = message.payload.decode("utf-8")
            chunk = message.topic.value.split('/')
            device = config.find_device_by_key(chunk)
            action = message.payload.decode('utf-8').lower()
            hex_commands = device.get_hex_command(action)
            state_topic = device.get_state_topic(chunk)
            state_key = device.get_state_key(chunk)
            command = Command(device,
                              hex_commands,
                              action,
                              [State(device.component, {state_key: action}, state_topic)],
                              device.get_ack(action))
            _LOGGER.info(f'payload => {payload} topic => {message.topic}')
            await config.command_queue.put(command)


async def mqtt_listener(config: RuntimeConfig):
    client = aiomqtt.Client(hostname=config.mqtt.host,
                            port=config.mqtt.port,
                            username=config.mqtt.user,
                            password=config.mqtt.password)
    while True:
        try:
            async with client:
                asyncio.ensure_future(asyncio.create_task(state_q_consumer(client, config)))
                await device_discovery(client, config.devices)
                await command_consumer(client, config)
        except aiomqtt.MqttError as e:
            _LOGGER.error(f'mqtt connection lost: {e.args}')
            await asyncio.sleep(5)
