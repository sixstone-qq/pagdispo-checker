"""Main application entry point
"""
import asyncio

from pagdispo.checker.config import load
from pagdispo.checker.monitor import monitor

def run():
    """Entry point for the website checker"""
    websites = load("websites.toml")

    loop = asyncio.get_event_loop()
    loop.run_until_complete(monitor(websites))
