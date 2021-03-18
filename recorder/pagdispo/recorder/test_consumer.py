import asyncio
import json
import random
import string
from datetime import datetime

import aiokafka
import pytest

from pagdispo.recorder.model import Website, WebsiteResult
from pagdispo.recorder.consumer import consume
from pagdispo.recorder.settings import settings


@pytest.fixture(scope='session')
def topic():
    return 'topic-{}'.format("".join(random.choice(string.ascii_letters) for _ in range(10)))


@pytest.fixture(scope='function')
async def kafka_producer():
    producer = aiokafka.AIOKafkaProducer(
        bootstrap_servers=settings.KAFKA_BROKERS)

    await producer.start()

    yield producer

    await producer.stop()


@pytest.mark.asyncio
async def test_consume(kafka_producer, topic, monkeypatch):
    """Send two messages and consume them"""
    # apply monkeypatch to settings to override the topic
    monkeypatch.setattr(settings, 'KAFKA_TOPIC', topic)

    queue = asyncio.Queue()
    task = asyncio.create_task(consume(queue))

    await asyncio.sleep(2)

    record = {'website': Website(id='id1', url='http://foo.org', method='GET').dict(),
              'result': WebsiteResult(website_id='id1',
                                      elapsed_time=0.2,
                                      status=200,
                                      at=datetime(2020, 3, 18, 23, 52)).dict()}

    for i in range(2):
        await kafka_producer.send_and_wait(topic,
                                           key=record['website']['id'].encode(),
                                           value=json.dumps(record, default=str).encode())

    # Wait for consumption
    try:
        await asyncio.wait_for(task, timeout=1.0)
    except asyncio.TimeoutError:
        pass

    for i in range(2):
        (got_website, got_website_result) = await queue.get()

        assert got_website.dict() == record['website']
        # Ignore at as it is msg.timestamp
        assert ignore_keys(got_website_result.dict(), 'at') == ignore_keys(record['result'], 'at')

        queue.task_done()

    await queue.join()


# Taken from:
# https://stackoverflow.com/questions/18064610/ignoring-an-element-from-a-dict-when-asserting-in-pytest
def ignore_keys(d, *args):
    d = dict(d)
    for k in args:
        del d[k]
    return d
