from abc import ABC, abstractmethod

from app.models.log_event import LogEvent


class BaseLogParser(ABC):
    """Abstract base for log parsers. Parsers produce a list of LogEvent from raw lines."""

    @property
    @abstractmethod
    def source_name(self) -> str:
        """Identifier for the log source (e.g. 'nginx', 'syslog')."""
        ...

    @abstractmethod
    def parse(self, lines: list[str]) -> list[LogEvent]:
        """Parse raw log lines into structured LogEvent list."""
        ...

    def can_handle(self, line: str) -> bool:
        """Return True if this parser can handle the given line (for auto-detection)."""
        return False
