"""Kafka consumer to receive messages from topic
"""
import asyncio
import json
import io

import aiokafka
from aiokafka.helpers import create_ssl_context

from pagdispo.recorder.model import Website, WebsiteResult
from pagdispo.recorder.settings import settings


async def consume(queue: asyncio.Queue):
    """Consume website results from Kafka topic to send them to a queue"""
    ssl_context = None
    security_protocol = 'PLAINTEXT'
    if settings.KAFKA_SSL_CAFILE is not None:
        ssl_context = create_ssl_context(
            cafile=settings.KAFKA_SSL_CAFILE,
            certfile=settings.KAFKA_SSL_CERTFILE,
            keyfile=settings.KAFKA_SSL_KEYFILE,
        )
        security_protocol = 'SSL'

    consumer = aiokafka.AIOKafkaConsumer(
        settings.KAFKA_TOPIC,
        bootstrap_servers=settings.KAFKA_BROKERS,
        group_id='website-monitor-recorder',
        # auto_offset_reset='earliest',
        key_deserializer=bytes.decode,
        value_deserializer=value_deserialiser,
        ssl_context=ssl_context,
        security_protocol=security_protocol,
    )
    await consumer.start()

    try:
        async for msg in consumer:
            try:
                website = Website(id=msg.key,
                                  url=msg.value['website']['url'],
                                  method=msg.value['website'].get('method', 'GET'),
                                  match_regex=msg.value['website'].get('match_regex'))
                website_result = WebsiteResult(website_id=msg.key,
                                               elapsed_time=msg.value['result']['elapsed_time'],
                                               status=msg.value['result']['status'],
                                               matched=msg.value['result'].get('matched'),
                                               at=msg.timestamp)

                await queue.put((website, website_result))
            except KeyError as ex:
                print('Wrong value: {} => {}'.format(msg.value, ex))

    finally:
        await consumer.stop()


def value_deserialiser(blob: bytes) -> dict:
    return json.load(io.BytesIO(blob))
