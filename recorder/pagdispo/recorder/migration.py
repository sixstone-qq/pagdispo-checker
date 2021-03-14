from yoyo import get_backend, read_migrations

from pagdispo.recorder.settings import settings


def run():
    """Entry point for SQL DB migrations"""

    backend = get_backend(settings.POSTGRESQL_DSN)
    migrations = read_migrations(str(settings.PROJ_ROOT / 'db' / 'migrations'))

    with backend.lock():
        # Apply any outstanding migrations
        backend.apply_migrations(backend.to_apply(migrations))

    print('Migration done!')
