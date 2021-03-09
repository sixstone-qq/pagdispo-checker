from unittest import mock

import aiohttp
import pytest

from pagdispo.checker.model import Website, WebsiteResult
from pagdispo.checker.monitor import fetch


@pytest.fixture
async def session(event_loop):
    session = aiohttp.ClientSession(loop=event_loop)
    yield session
    await session.close()


@pytest.mark.asyncio
async def test_head_fetch(session):
    website = Website(url='http://foo.org', method='HEAD')
    with mock.patch.object(session, 'request') as patched:
        patched.return_value.__aenter__.return_value.status = 200
        res = await fetch(session, website)
        assert res == (website, WebsiteResult(elapsed_time=0.0, status=200))

    assert patched.call_count == 1
    assert patched.call_args.args == (website.method, website.url)
    # Make sure the text hasn't been called
    assert patched.return_value.__aenter__.return_value.text.called is False


@pytest.mark.asyncio
async def test_get_fetch(session):
    website = Website(url='http://bar.org', match_regex='re')
    with mock.patch.object(session, 'request') as patched:
        patched.return_value.__aenter__.return_value.status = 200
        patched.return_value.__aenter__.return_value.text.return_value = 'reee'
        res = await fetch(session, website)
        assert res == (website, WebsiteResult(elapsed_time=0.0, status=200, matched=True))

    assert patched.call_count == 1
    assert patched.call_args.args == (website.method, website.url)
    assert patched.return_value.__aenter__.return_value.text.called is True
