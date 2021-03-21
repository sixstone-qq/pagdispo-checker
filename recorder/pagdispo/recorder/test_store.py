import os
import socket
import time
from datetime import datetime

import aiopg
import psycopg2
import pytest
import yoyo
from docker import APIClient

from pagdispo.recorder.settings import proj_root, Settings
from pagdispo.recorder.model import Website, WebsiteResult
from pagdispo.recorder.store import insert_check


@pytest.fixture(scope='session')
def settings():
    return Settings(_env_file=str(proj_root() / 'testing.env'))


@pytest.fixture(scope='session')
def unused_port():
    def f():
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('127.0.0.1', 0))
            return s.getsockname()[1]

    return f


@pytest.fixture(scope='session')
def docker():
    return APIClient(version='auto')


@pytest.fixture(scope='session')
def pg_server(unused_port, docker):
    if 'CI' not in os.environ:
        yield
        return

    docker.pull('postgres:12')

    container_args = dict(
        image='postgres:12',
        name='aiopg-test-server',
        ports=[5432],
        detach=True,
    )

    # bound IPs do not work on OSX
    host = "127.0.0.1"
    host_port = unused_port()
    container_args['host_config'] = docker.create_host_config(
        port_bindings={5432: (host, host_port)}
    )
    container_args['environment'] = {'POSTGRES_HOST_AUTH_METHOD': 'trust'}

    container = docker.create_container(**container_args)

    try:
        docker.start(container=container['Id'])
        server_params = dict(database='postgres',
                             user='postgres',
                             password='mysecretpassword',
                             host=host,
                             port=host_port)
        delay = 0.001
        for i in range(100):
            try:
                conn = psycopg2.connect(**server_params)
                cur = conn.cursor()
                cur.execute("CREATE EXTENSION hstore;")
                cur.close()
                conn.close()
                break
            except psycopg2.Error:
                time.sleep(delay)
                delay *= 2
        else:
            pytest.fail("Cannot start postgres server")

        container['host'] = host
        container['port'] = host_port
        container['pg_params'] = server_params

        yield container
    finally:
        docker.kill(container=container['Id'])
        docker.remove_container(container['Id'])


@pytest.fixture(scope='session')
def pg_params(settings, pg_server):
    if 'CI' in os.environ:
        return dict(**pg_server['pg_params'])

    return dict(dsn=settings.POSTGRESQL_DSN)


@pytest.fixture(scope='session')
def db_creation(pg_params, settings):
    """Set the DB connection and create a DB"""
    path = settings.POSTGRESQL_DSN.path
    db_name = path[1:]
    if 'CI' not in os.environ:
        conn = psycopg2.connect(str(settings.POSTGRESQL_DSN.replace(path, '/postgres')))
        conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
        with conn.cursor() as cur:
            cur.execute("CREATE DATABASE " + db_name)

    # Run migrations
    dsn = settings.POSTGRESQL_DSN
    if 'CI' in os.environ:
        dsn = 'postgres://{}:{}@{}:{}/{}'.format(pg_params['user'],
                                                 pg_params['password'],
                                                 pg_params['host'],
                                                 pg_params['port'],
                                                 pg_params['database'])

    backend = yoyo.get_backend(dsn)
    migrations = yoyo.read_migrations(str(settings.PROJ_ROOT / 'db' / 'migrations'))

    with backend.lock():
        # Apply any outstanding migrations
        backend.apply_migrations(backend.to_apply(migrations))

    backend._connection.close()

    yield

    if 'CI' not in os.environ:
        with conn.cursor() as cur:
            cur.execute('DROP DATABASE IF EXISTS  ' + db_name)

        conn.close()


@pytest.fixture(scope='function')
async def db_pool(db_creation, settings, pg_params):
    async with aiopg.create_pool(**pg_params) as pool:
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
