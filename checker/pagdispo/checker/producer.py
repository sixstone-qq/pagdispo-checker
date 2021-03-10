"""Kafka producer to send messages to topic received via queue"""
import asyncio

import aiokafka
from pydantic import BaseModel

from pagdispo.checker.model import Website, WebsiteResult
from pagdispo.checker.settings import settings


async def produce(queue: asyncio.Queue) -> None:
    producer = aiokafka.AIOKafkaProducer(
        bootstrap_servers=settings.KAFKA_BROKERS)

    await producer.start()

    try:
        while True:
            # It comprises of a tuple (Website, WebsiteResult)
            website_output = await queue.get()

            if len(website_output) == 2:
                kafka_record = KafkaRecord(website=website_output[0], result=website_output[1])
                await producer.send_and_wait('website.monitor',
                                             key=website_output[0].id.encode(),
                                             value=kafka_record.json().encode())

                print('Sent {}'.format(website_output[0].id))
            else:
                print('Invalid data')

            queue.task_done()
    finally:
        await producer.stop()


class KafkaRecord(BaseModel):
    website: Website
    result: WebsiteResult
