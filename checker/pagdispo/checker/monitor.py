import asyncio
from typing import Sequence, Tuple

import aiohttp

from pagdispo.checker.model import HTTPMethodEnum, Website, WebsiteResult


async def monitor_forever(websites: Sequence[Website], queue: asyncio.Queue) -> None:
    while True:
        await monitor(websites, queue)
        await asyncio.sleep(1.0)


async def monitor(websites: Sequence[Website], queue: asyncio.Queue) -> None:
    """Monitor all websites and send them to a queue"""
    # Defines tracing for calc the elapsed time
    trace_cfg = aiohttp.TraceConfig()
    trace_cfg.on_request_start.append(on_request_start)
    trace_cfg.on_request_end.append(on_request_end)
    # We can modify the parallel limit with a custom TCPConnector
    async with aiohttp.ClientSession(trace_configs=[trace_cfg]) as session:
        futures = [fetch(session, w) for w in websites]
        for coro in asyncio.as_completed(futures):
            # Send messages to queue as they come
            website_out = await coro
            await queue.put(website_out)


async def fetch(session: aiohttp.ClientSession, website: Website) -> Tuple[Website, WebsiteResult]:
    """Fetch website monitor data from a website monitor spec"""
    print('Querying: {}'.format(website.url))
    trace = {'elapsed': 0.0}
    async with session.request(website.method, website.url, trace_request_ctx=trace) as resp:
        website_result = WebsiteResult(elapsed_time=trace['elapsed'], status=resp.status)
        print('Code: {}'.format(resp.status))
        print('Elapsed: {}'.format(trace))
        if website.method == HTTPMethodEnum.HEAD or website.match_regex is None:
            return (website, website_result)

        content = await resp.text()
        match = website.match_regex.search(content)
        print('Match "{}": {}'.format(website.match_regex.pattern, match is not None))
        website_result.matched = match is not None
        return (website, website_result)


async def on_request_start(session, trace_config_ctx, params):
    trace_config_ctx.start = asyncio.get_event_loop().time()


async def on_request_end(session, trace_config_ctx, params):
    trace_config_ctx.trace_request_ctx['elapsed'] = asyncio.get_event_loop().time() - trace_config_ctx.start
