"""Config loading
"""
from typing import Sequence

import toml

from pagdispo.checker.model import Website


def load(path: str) -> Sequence[Website]:
    """
    Load a configuration file to get the list of servers to check

    [[websites]]
    url = http://foo.bar
    method = GET
    match_regex = 'OK$'


    :param str path: the relative path of the file in TOML format
    :returns: the list of servers to check
    :rtype: Sequence[Server]

    :raises Exception: if no websites are found
    :raises pydantic.ValidationError: if there is any website configuration error
    """
    with open(path, 'r') as f:
        cfg = toml.load(f)

    if 'websites' not in cfg:
        raise Exception("no websites found")

    websites = []
    for website in cfg['websites']:
        kwargs = {}
        for attr in ('url', 'method', 'match_regex'):
            if attr in website:
                kwargs[attr] = website[attr]

        websites.append(Website(**kwargs))

    return tuple(websites)
