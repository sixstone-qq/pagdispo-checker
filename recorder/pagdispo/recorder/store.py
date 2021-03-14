"""Store of the website monitor results"""
import asyncio

import aiopg

from pagdispo.recorder.model import Website, WebsiteResult
from pagdispo.recorder.settings import settings


async def store(queue: asyncio.Queue) -> None:
    pool = await aiopg.create_pool(
        dbname=settings.POSTGRESQL_DSN.path[1:],
        user=settings.POSTGRESQL_DSN.user,
        host=settings.POSTGRESQL_DSN.host,
    )

    try:
        while True:
            # It comprises of a tuple (Website, WebsiteResult)
            website_output = await queue.get()

            if len(website_output) == 2:
                await insert_check(pool, *website_output)
            else:
                print('Invalid data: {}'.format(website_output))

            queue.task_done()
    finally:
        pool.close()


async def insert_check(conn: aiopg.Pool, website: Website, website_result: WebsiteResult) -> None:
    with (await conn.cursor()) as cur:
        async with cur.begin():
            await cur.execute("""
               INSERT INTO websites(id, url, method, match_regex) VALUES
               (%(id)s, %(url)s, %(method)s, %(match_regex)s)
               ON CONFLICT DO NOTHING;
               """,
                              {'id': website.id,
                               'url': str(website.url),
                               'method': website.method.name,
                               'match_regex': website.match_regex.pattern
                               if website.match_regex is not None else None}
                              )
            print('Added website rows: {}'.format(cur.rowcount))

            await cur.execute("""
               INSERT INTO websites_results(website_id, elapsed_time, status, matched, at) VALUES
               (%(id)s, %(elapsed_time)s, %(status)s, %(matched)s, %(at)s)
               ON CONFLICT DO NOTHING;
               """,
                              {'id': website_result.website_id,
                               'elapsed_time': website_result.elapsed_time,
                               'status': website_result.status,
                               'matched': website_result.matched,
                               'at': website_result.at}
                              )
            print('Added website results: {}'.format(cur.rowcount))
