"""Main application entry point
"""
import asyncio

from pagdispo.recorder.consumer import consume
from pagdispo.recorder.store import store


async def main():
    """App main program:

    * It launches two tasks (consumer & store)
    * Connected via queue
    """
    queue = asyncio.Queue()

    consume_task = asyncio.create_task(consume(queue))
    store_task = asyncio.create_task(store(queue))

    await asyncio.gather(consume_task, store_task)


def run():
    """Entry point for the website monitor recorder"""
    asyncio.run(main())


if __name__ == '__main__':
    run()
