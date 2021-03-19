# pagdispo

`pagdispo` (_página disponible_ available website in Spanish) is a
Python system to monitor websites periodically in a scalable way.

It comprises of two Python applications: `pagdispo-checker` and
`pagdispo-recorder`.

### pagdispo-checker

`pagdispo-checker` is a Python app that reads from a [TOML](https://toml.io/en/) file the websites to monitor
optionally matching a regular expression. It follows this format:

```toml
[[websites]]

url = "https://awesome.web.com"
method = "HEAD"  # "GET" or "HEAD" are available

[[websites]]

url = "https://another.awesome.web.com/placebo"
match_regex = "tumbles?"
#method = "GET" by default
```

It peridiocally checks the availability of those websites,
configurable via `TICK_TIME` environment variable and send to a Kafka
topic configurable via `KAFKA_TOPIC` through broker configurable via
`KAFKA_BROKERS` the result of the monitor check.

### pagdispo-recorder

`pagdispo-recorder` is a Python app that reads from a Kafka topic
configurable via `KAFKA_TOPIC` environment variable through a Kafka
broker via `KAFKA_BROKERS` the results of monitor checks of websites
and stores them in a PostgreSQL database whose DSN is configurable via
`POSTGRESQL_DSN` environment variable.

## Development

It provides a Docker compose with a Kafka + PostgreSQL ready to be
use. `Virtualenv` is used to set up the development locally.

```shell
make start-dev
```

Then, run `cd checker && ./venv/bin/pagdispo-checker` for local
testing in one terminal and `cd recorder &&
./venv/bin/pagdipso-recorder` in other terminal.

In order to stop the docker compose, run `make stop-dev`.

## Testing

You can run all testsuite using the created virtualenv:

```shell
make start-dev
make test
```

## Linting

[flake8](https://flake8.pycqa.org/en/latest/) is used for style guide
enforcement or linting and
[MyPy](https://mypy.readthedocs.io/en/stable/index.html) for
informative static type checking on python 3 annotations.

You can run
```
make lint
```

To see their results.

## Settings

The configuration settings can be modified using environment variables
or via dotenv files.

For example:

```
KAFKA_BROKERS=1.1.1.1:9092 python -m pagdispo.checker
```

Available settings for
[pagdispo-checker](checker/pagdispo/checker/settings.py) and [pagdispo-recorder](recorder/pagdispo/recorder/settings.py).
