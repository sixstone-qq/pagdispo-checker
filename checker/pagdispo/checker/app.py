"""Main application entry point
"""
import asyncio
from typing import Sequence

from pagdispo.checker.config import load
from pagdispo.checker.model import Website
from pagdispo.checker.monitor import monitor_forever
from pagdispo.checker.producer import produce


async def main(websites: Sequence[Website]) -> None:
    """App main program:

    * It launches two tasks (monitor & producer)
    * Connected via queue
    """
    queue = asyncio.Queue()

    monitor_task = asyncio.create_task(monitor_forever(websites, queue))
    producer_task = asyncio.create_task(produce(queue))

    await asyncio.gather(monitor_task, producer_task)


def run():
    """Entry point for the website checker"""
    websites = load("websites.toml")

    asyncio.run(main(websites))


if __name__ == '__main__':
    run()
