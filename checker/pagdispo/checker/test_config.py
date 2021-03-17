import builtins
import os
from io import StringIO

import pydantic
import pytest

from .config import load
from .model import Website


def test_empty_config(mockopen):
    filename = 'empty.toml'
    mockopen.write(filename, "")

    with pytest.raises(Exception):
        load(filename)


def test_valid_config(mockopen):
    filename = 'valid.toml'
    mockopen.write(filename, """
    [[websites]]
    url = "http://foo.org"

    [[websites]]
    url = "https://duckduckgo.com/search"
    method = "GET"
    match_regex = "duck$"

    [[websites]]
    url = "http://only-heads.org"
    method = "HEAD"
    match_regex = "foobar.*"
    """)

    website_list = load(filename)
    assert website_list == (Website(url='http://foo.org', method='GET'),
                            Website(url='https://duckduckgo.com/search', match_regex='duck$'),
                            Website(url='http://only-heads.org', method='HEAD',
                                    match_regex='foobar.*'))


def test_invalid_input(mockopen):
    filename = 'invalid_input.toml'

    cases = (
        """
        [[websites]]
        """,
        """
        [[websites]]
        url = "foo"
        """,
        """
        [[websites]]
        url = "http://foo.org"
        method = "POST"
        """,
        """
        [[websites]]
        url = "http://foo.org"
        method = "HEAD"
        match_regex = "["
        """)

    for subcase in cases:
        mockopen.write(filename, subcase)
        with pytest.raises(pydantic.ValidationError):
            load(filename)


# Taken from https://gist.github.com/curzona/0616d4752f44f2ff8914
class MockFileManager():
    def __init__(self):
        self.files = {}
        self._open = builtins.open

    def open(self, name, mode='r', buffering=-1, **options):
        name = os.path.abspath(name)
        if mode.startswith('r') and name not in self.files:
            # We have to let some files through
            return self._open(name, mode, buffering, **options)

        if mode.startswith('w') or \
           (mode.startswith('a') and name not in self.files):
            buf = StringIO()
            buf.close = lambda: None
            self.files[name] = buf

        buf = self.files[name]

        if mode.startswith('r'):
            buf.seek(0)
        elif mode.startswith('a'):
            buf.seek(0)

        return buf

    def write(self, name, text):
        name = os.path.abspath(name)
        buf = StringIO(text)
        buf.close = lambda: None
        self.files[name] = buf

    def read(self, name):
        name = os.path.abspath(name)
        if name not in self.files:
            raise IOError(2, "No such file or directory: '%s'" % name)

        return self.files[name].getvalue()


@pytest.fixture
def mockopen(monkeypatch):
    manager = MockFileManager()
    monkeypatch.setattr(builtins, 'open', manager.open)
    return manager
