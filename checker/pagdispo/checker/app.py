"""Main application entry point
"""
from .config import load

def run():
    """Entry point for the website checker"""
    print(load("websites.toml"))
