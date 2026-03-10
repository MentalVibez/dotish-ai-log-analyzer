import re
from datetime import datetime
from app.models.log_event import LogEvent, LogLevel
from app.parsers.base_parser import BaseLogParser

# Nginx error log: 2024/01/15 12:00:00 [error] 1234#0: message
# Or: 2024/01/15 12:00:00 [warn] ...
NGINX_ERROR_LINE = re.compile(
    r"^(?P<date>\d{4}/\d{2}/\d{2}\s+\d{2}:\d{2}:\d{2})\s+\[(?P<level>\w+)\]\s+(?P<message>.+)$"
)

# Nginx access: IP - - [day/month/year:time zone] "method path" status size ...
NGINX_ACCESS_LINE = re.compile(
    r'^\S+\s+\S+\s+\S+\s+\[([^\]]+)\]\s+"[^"]*"\s+(?P<status>\d+)\s+.+$'
)


class NginxParser(BaseLogParser):
    @property
    def source_name(self) -> str:
        return "nginx"

    def can_handle(self, line: str) -> bool:
        stripped = line.strip()
        if NGINX_ERROR_LINE.match(stripped):
            return True
        if NGINX_ACCESS_LINE.match(stripped):
            return True
        return False

    def _parse_timestamp(self, s: str) -> datetime | None:
        try:
            return datetime.strptime(s.strip(), "%Y/%m/%d %H:%M:%S")
        except ValueError:
            return None

    def _parse_access_timestamp(self, s: str) -> datetime | None:
        # e.g. 15/Jan/2024:12:00:00 +0000
        try:
            return datetime.strptime(s.split(" ")[0], "%d/%b/%Y:%H:%M:%S")
        except (ValueError, IndexError):
            return None

    def _level_from_nginx(self, level: str) -> LogLevel:
        level_lower = level.lower()
        if level_lower in ("error", "crit", "alert", "emerg"):
            return LogLevel.ERROR
        if level_lower == "warn":
            return LogLevel.WARNING
        if level_lower in ("info", "notice"):
            return LogLevel.INFO
        if level_lower == "debug":
            return LogLevel.DEBUG
        return LogLevel.UNKNOWN

    def parse(self, lines: list[str]) -> list[LogEvent]:
        events: list[LogEvent] = []
        for raw in lines:
            line = raw.strip()
            if not line:
                continue
            # Try error log format first
            m = NGINX_ERROR_LINE.match(line)
            if m:
                ts = self._parse_timestamp(m.group("date"))
                level = self._level_from_nginx(m.group("level"))
                events.append(
                    LogEvent(
                        timestamp=ts,
                        level=level,
                        message=m.group("message").strip(),
                        source=self.source_name,
                        raw=raw,
                    )
                )
                continue
            # Try access log; treat 5xx as error, 4xx as warning
            m = NGINX_ACCESS_LINE.match(line)
            if m:
                status = int(m.group("status"))
                if status >= 500:
                    level = LogLevel.ERROR
                elif status >= 400:
                    level = LogLevel.WARNING
                else:
                    level = LogLevel.INFO
                ts = self._parse_access_timestamp(m.group(1))
                events.append(
                    LogEvent(
                        timestamp=ts,
                        level=level,
                        message=f"HTTP {status}",
                        source=self.source_name,
                        raw=raw,
                    )
                )
        return events
