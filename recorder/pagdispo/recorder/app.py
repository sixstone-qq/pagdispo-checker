"""Main application entry point
"""
import asyncio

from pagdispo.recorder.consumer import consume


async def main():
    """App main program:

    * It launches two tasks (consumer & store)
    * Connected via queue
    """
    queue = asyncio.Queue()

    await consume(queue)


def run():
    """Entry point for the website monitor recorder"""
    asyncio.run(main())
