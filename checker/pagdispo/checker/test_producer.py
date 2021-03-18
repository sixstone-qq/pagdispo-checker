import asyncio
import random
import string
from datetime import datetime

import aiokafka
import pytest

from pagdispo.checker.model import Website, WebsiteResult
from pagdispo.checker.producer import get_and_send
from pagdispo.checker.settings import settings


@pytest.fixture(scope='session')
def topic():
    return 'topic-{}'.format("".join(random.choice(string.ascii_letters) for _ in range(10)))


@pytest.fixture(scope='function')
async def kafka_consumer(topic):
    """Set the Kafka connection"""
    consumer = aiokafka.AIOKafkaConsumer(
        topic,
        bootstrap_servers=settings.KAFKA_BROKERS,
        auto_offset_reset='earliest',
        key_deserializer=bytes.decode,
    )

    await consumer.start()

    yield consumer

    await consumer.stop()


@pytest.fixture(scope='function')
async def kafka_producer():
    producer = aiokafka.AIOKafkaProducer(
        bootstrap_servers=settings.KAFKA_BROKERS)

    await producer.start()

    yield producer

    await producer.stop()


@pytest.mark.asyncio
async def test_get_and_send(kafka_producer, kafka_consumer, topic):
    """Send two messages and consume them"""
    queue = asyncio.Queue()

    website = Website(id='id1', url='http://foo.org', method='GET')
    website_result = WebsiteResult(website_id='id1',
                                   elapsed_time=0.2,
                                   status=200,
                                   at=datetime(2020, 3, 18, 23, 6))

    queue.put_nowait((website, website_result))
    queue.put_nowait((website, website_result))

    for i in range(2):
        res = await get_and_send(queue, kafka_producer, topic)
        assert res

        # Consume that event
        msg = await kafka_consumer.getone()

        assert msg.key == website.id
        assert msg.value.decode() == "".join(
            ("""{"website": """, website.json(),
             ', "result": ', website_result.json(), '}'))

    await queue.join()
