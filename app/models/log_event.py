from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


class LogLevel(str, Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    DEBUG = "debug"
    UNKNOWN = "unknown"


class LogEvent(BaseModel):
    timestamp: datetime | None = None
    level: LogLevel = LogLevel.UNKNOWN
    message: str = ""
    source: str = ""
    raw: str = Field(default="", description="Original log line")

