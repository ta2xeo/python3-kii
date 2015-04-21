from enum import Enum, unique


@unique
class Site(Enum):
    US = ''
    CN = '-cn2'
    JP = '-jp'
    SG = '-sg'


@unique
class UserRequestType(Enum):
    by_address = 1
    by_id = 2
    by_me_literal = 3
