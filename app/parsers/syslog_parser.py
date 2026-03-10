import re
from datetime import datetime
from app.models.log_event import LogEvent, LogLevel
from app.parsers.base_parser import BaseLogParser

# RFC 5424: <PRI>VERSION TIMESTAMP HOSTNAME APP-NAME PROCID MSGID STRUCTURED-DATA MESSAGE
# PRI = facility*8 + severity (0-7: emerg=0, alert=1, crit=2, err=3, warning=4, notice=5, info=6, debug=7)
SYSLOG_RFC5424 = re.compile(
    r"^<(?P<pri>\d+)>(?P<version>\d+)\s+(?P<timestamp>\S+)\s+(?P<hostname>\S+)\s+"
    r"(?P<app>\S+)\s+(?P<procid>\S+)\s+(?P<msgid>\S+)\s+(?P<sd>\S*)\s*(?P<message>.*)$"
)

# BSD-style: TIMESTAMP HOSTNAME TAG: MESSAGE  e.g. Jan 15 12:00:00 host myapp: message
SYSLOG_BSD = re.compile(
    r"^(?P<timestamp>\w{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})\s+(?P<hostname>\S+)\s+"
    r"(?P<tag>[^:]+):\s*(?P<message>.*)$"
)


def _severity_from_pri(pri: int) -> LogLevel:
    severity = pri & 0x07
    if severity <= 2:
        return LogLevel.ERROR
    if severity == 3:
        return LogLevel.ERROR
    if severity == 4:
        return LogLevel.WARNING
    if severity == 5:
        return LogLevel.INFO
    if severity >= 6:
        return LogLevel.DEBUG
    return LogLevel.UNKNOWN


class SyslogParser(BaseLogParser):
    @property
    def source_name(self) -> str:
        return "syslog"

    def can_handle(self, line: str) -> bool:
        stripped = line.strip()
        if stripped.startswith("<") and SYSLOG_RFC5424.match(stripped):
            return True
        if SYSLOG_BSD.match(stripped):
            return True
        return False

    def _parse_bsd_timestamp(self, s: str, year: int | None = None) -> datetime | None:
        # Jan 15 12:00:00 - no year in BSD, use current or provided
        try:
            yr = year or datetime.now().year
            dt = datetime.strptime(f"{s} {yr}", "%b %d %H:%M:%S %Y")
            return dt
        except ValueError:
            return None

    def parse(self, lines: list[str]) -> list[LogEvent]:
        events: list[LogEvent] = []
        for raw in lines:
            line = raw.strip()
            if not line:
                continue
            # RFC 5424
            m = SYSLOG_RFC5424.match(line)
            if m:
                pri = int(m.group("pri"))
                level = _severity_from_pri(pri)
                message = (m.group("message") or "").strip()
                events.append(
                    LogEvent(
                        timestamp=None,  # could parse ISO timestamp from m.group("timestamp")
                        level=level,
                        message=message or m.group(0),
                        source=self.source_name,
                        raw=raw,
                    )
                )
                continue
            # BSD
            m = SYSLOG_BSD.match(line)
            if m:
                ts = self._parse_bsd_timestamp(m.group("timestamp"))
                message = (m.group("message") or "").strip()
                # Heuristic: elevate level if message contains error/warn
                level = LogLevel.INFO
                msg_lower = message.lower()
                if (
                    "error" in msg_lower
                    or "err" in msg_lower
                    or "critical" in msg_lower
                    or "refused" in msg_lower
                    or "failed" in msg_lower
                ):
                    level = LogLevel.ERROR
                elif "warn" in msg_lower or "warning" in msg_lower:
                    level = LogLevel.WARNING
                events.append(
                    LogEvent(
                        timestamp=ts,
                        level=level,
                        message=message or line,
                        source=self.source_name,
                        raw=raw,
                    )
                )
        return events
