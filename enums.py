from enum import Enum

class typeEnum(Enum):
    STOP = 1
    END = 2
    START = 3
    COMMAND = 4
    WEATHER = 5
    NEWS = 6
    NEXT_NEWS = 7
    PREVIOUS_NEWS = 8
    EXPAND_NEWS = 9
    CLEAR_BUFFER = 10

class languageEnum(Enum):
    ENGLISH = 1
    POLISH = 2