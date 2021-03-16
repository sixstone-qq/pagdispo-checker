# pagdispo

`pagdispo` (_página disponible_ available website in Spanish) is a
Python system to monitor websites periodically in a scalable way.

It comprises of two Python applications: `pagdispo-checker` and
`pagdispo-recorder`.

## pagdispo-checker

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

## pagdispo-recorder

`pagdispo-recorder` is a Python app that reads from a Kafka topic
configurable via `KAFKA_TOPIC` environment variable through a Kafka
broker via `KAFKA_BROKERS` the results of monitor checks of websites
and stores them in a PostgreSQL database whose DSN is configurable via
`POSTGRESQL_DSN` environment variable.


