from enum import Enum
from sre_constants import SUCCESS


class UserStatus(Enum):
    ACTIVE = 1
    BLOCKED = 2


class Status(Enum):
    UNKNOWN = 'UNKNWON'
    SUCCESS = 'SUCCESS'
    ERROR = 'ERROR'
    FAILED = 'FAILED'
    VALIDATION_FAILED = 'VALIDATION_FAILED'
    NOT_FOUND = 'NOT_FOUND'


class PaginationSetting(Enum):
    DEFAULT_PAGE_NUMBER = 1
    DEFAULT_PAGE_SIZE = 10


class DateStringFormat(Enum):
    ISO_FORMAT = '%Y-%m-%dT%H:%M:%S.%fZ'


class PostType(Enum):
    Question = 'question'
    Answer = 'answer'