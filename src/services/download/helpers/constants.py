from enum import Enum


class DownloadStatus(Enum):
    STARTED = int("e8f30b", 16)
    RUNNING = int("f3ad0b", 16)
    DONE = int("0dba2f", 16)
    ERROR = int("f63106", 16)
    CANCELED = int("510666", 16)
