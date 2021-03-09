from enum import Enum
from typing import Optional, Pattern

from pydantic import BaseModel, HttpUrl


class HTTPMethodEnum(str, Enum):
    GET = 'GET'
    HEAD = 'HEAD'


class Website(BaseModel):
    """Website defines the website to monitor"""
    url: HttpUrl
    method: HTTPMethodEnum = HTTPMethodEnum.GET
    match_regex: Optional[Pattern]


class WebsiteResult(BaseModel):
    """WebsiteResult defines the result of a website monitor result"""
    elapsed_time: float
    status: int
    matched: Optional[bool]
