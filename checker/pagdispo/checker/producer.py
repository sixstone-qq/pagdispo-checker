"""Kafka producer to send messages to topic received via queue"""
import asyncio

import aiokafka
from aiokafka.helpers import create_ssl_context
from pydantic import BaseModel

from pagdispo.checker.model import Website, WebsiteResult
from pagdispo.checker.settings import settings


async def produce(queue: asyncio.Queue) -> None:
    ssl_context = None
    security_protocol = 'PLAINTEXT'
    if settings.KAFKA_SSL_CAFILE is not None:
        ssl_context = create_ssl_context(
            cafile=settings.KAFKA_SSL_CAFILE,
            certfile=settings.KAFKA_SSL_CERTFILE,
            keyfile=settings.KAFKA_SSL_KEYFILE,
        )
        security_protocol = 'SSL'

    producer = aiokafka.AIOKafkaProducer(
        bootstrap_servers=settings.KAFKA_BROKERS,
        ssl_context=ssl_context,
        security_protocol=security_protocol,
    )

    print(ssl_context)

    await producer.start()

    try:
        while True:
            await get_and_send(queue, producer, settings.KAFKA_TOPIC)
    finally:
        await producer.stop()


async def get_and_send(queue: asyncio.Queue,
                       producer: aiokafka.AIOKafkaProducer,
                       topic: str) -> bool:
    # It comprises of a tuple (Website, WebsiteResult)
    website_output = await queue.get()

    sent = False
    if len(website_output) == 2:
        kafka_record = KafkaRecord(website=website_output[0], result=website_output[1])
        await producer.send_and_wait(topic,
                                     key=website_output[0].id.encode(),
                                     value=kafka_record.json().encode())

        print('Sent {}'.format(website_output[0].id))
        sent = True
    else:
        print('Invalid data')

    queue.task_done()
    return sent


class KafkaRecord(BaseModel):
    website: Website
    result: WebsiteResult
