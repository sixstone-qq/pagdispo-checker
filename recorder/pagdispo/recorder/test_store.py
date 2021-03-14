from datetime import datetime

import aiopg
import psycopg2
import pytest
import yoyo

from pagdispo.recorder.settings import proj_root, Settings
from pagdispo.recorder.model import Website, WebsiteResult
from pagdispo.recorder.store import insert_check


@pytest.fixture(scope='session')
def settings():
    return Settings(_env_file=str(proj_root() / 'testing.env'))


@pytest.fixture(scope='session')
def db_conn(settings):
    """Set the DB connection and create a DB"""
    db_name = settings.POSTGRESQL_DSN.path[1:]
    conn = psycopg2.connect(dbname='postgres',
                            user=settings.POSTGRESQL_DSN.user,
                            host=settings.POSTGRESQL_DSN.host)
    conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
    with conn.cursor() as cur:
        cur.execute("CREATE DATABASE " + db_name)

    # Run migrations
    backend = yoyo.get_backend(settings.POSTGRESQL_DSN)
    migrations = yoyo.read_migrations(str(settings.PROJ_ROOT / 'db' / 'migrations'))

    with backend.lock():
        # Apply any outstanding migrations
        backend.apply_migrations(backend.to_apply(migrations))

    backend._connection.close()

    yield conn

    with conn.cursor() as cur:
        cur.execute('DROP DATABASE IF EXISTS  ' + db_name)

    conn.close()


@pytest.fixture(scope='function')
async def db_pool(db_conn, settings):
    async with aiopg.create_pool(dbname=settings.POSTGRESQL_DSN.path[1:],
                                 user=settings.POSTGRESQL_DSN.user,
                                 host=settings.POSTGRESQL_DSN.host) as pool:
        yield pool


@pytest.fixture(scope='function')
async def cursor(db_pool: aiopg.Pool) -> aiopg.Cursor:
    """This returns a cursor to a created db with its schema"""
    with (await db_pool.cursor()) as cursor:
        yield cursor


@pytest.fixture(scope='function')
def website() -> Website:
    return Website(id='id1', url='http://foo.org', method='GET')


@pytest.mark.asyncio
async def test_insert_check_content(db_pool: aiopg.Pool,
                                    cursor: aiopg.Cursor,
                                    website: Website) -> None:
    """Do insert_check and check content afterwards"""
    website_result = WebsiteResult(website_id='id1',
                                   elapsed_time=0.2,
                                   status=200,
                                   at=datetime(2020, 3, 14, 17, 15))
    await insert_check(db_pool, website, website_result)

    await cursor.execute('SELECT id, url, method, match_regex FROM websites WHERE id = %s',
                         (website.id,))
    res = await cursor.fetchall()
    assert len(res) == 1
    assert res[0] == (website.id, website.url, website.method, None)

    await cursor.execute("""
                         SELECT website_id, elapsed_time, status, matched, at
                         FROM websites_results
                         WHERE website_id = %s""",
                         (website.id,))
    res = await cursor.fetchall()
    assert len(res) == 1
    assert res[0] == (website_result.website_id,
                      website_result.elapsed_time,
                      website_result.status,
                      None,
                      website_result.at)


@pytest.mark.asyncio
async def test_insert_check_two_results(db_pool: aiopg.Pool,
                                        cursor: aiopg.Cursor,
                                        website: Website) -> None:
    """Test content two results"""
    website_result = WebsiteResult(website_id=website.id,
                                   elapsed_time=0.2,
                                   status=200,
                                   at=datetime(2020, 3, 14, 17, 15))
    await insert_check(db_pool, website, website_result)
    # Repeat same result
    await insert_check(db_pool, website, website_result)

    website_result_2 = WebsiteResult(website_id=website.id,
                                     elapsed_time=0.15,
                                     status=200,
                                     at=datetime(2020, 3, 14, 17, 20))
    await insert_check(db_pool, website, website_result_2)

    await cursor.execute('SELECT COUNT(*) FROM websites WHERE id = %s', (website.id,))
    res = await cursor.fetchone()
    assert res == (1,)

    await cursor.execute('SELECT COUNT(*) FROM websites_results WHERE website_id = %s',
                         (website.id,))
    res = await cursor.fetchone()
    assert res == (2,)
