from enum import Enum
from hashlib import blake2b
from typing import Optional, Pattern

from pydantic import BaseModel, HttpUrl, validator


class HTTPMethodEnum(str, Enum):
    GET = 'GET'
    HEAD = 'HEAD'


class Website(BaseModel):
    """Website defines the website to monitor"""
    url: HttpUrl
    method: HTTPMethodEnum = HTTPMethodEnum.GET
    match_regex: Optional[Pattern]
    id: str = None

    @validator('id', pre=True, always=True)
    def validate_id(cls, value, values):
        """This will set the id value derived from other values"""
        h = blake2b(digest_size=12)
        if 'url' not in values:
            # The model is already invalid
            raise ValueError
        h.update(str(values['url']).encode())
        h.update(str(values.get('method', 'GET')).encode())
        if values.get('match_regex') is not None:
            h.update(values['match_regex'].pattern.encode())
        return h.hexdigest()


class WebsiteResult(BaseModel):
    """WebsiteResult defines the result of a website monitor result"""
    elapsed_time: float
    status: int
    matched: Optional[bool]
