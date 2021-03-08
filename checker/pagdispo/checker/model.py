from enum import Enum
from typing import Optional, Pattern

from pydantic import BaseModel, HttpUrl

class HTTPMethodEnum(str, Enum):
    GET = 'GET'
    HEAD = 'HEAD'

class Website(BaseModel):
    """Website defines the model to use"""
    url: HttpUrl
    method: HTTPMethodEnum = HTTPMethodEnum.GET
    match_regex: Optional[Pattern]

    
    
