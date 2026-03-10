import json
import re
from datetime import datetime

from app.models.log_event import LogEvent, LogLevel
from app.parsers.base_parser import BaseLogParser

# Docker JSON log: {"log":"message\n","stream":"stdout","time":"2024-01-15T12:00:00.123456789Z"}
# Docker raw (when driver doesn't use JSON): 2024-01-15T12:00:00.123456789Z stdout F message
DOCKER_RAW_LINE = re.compile(
    r"^(?P<timestamp>\d{4}-\d{2}-\d{2}T[\d.:]+Z)\s+(?P<stream>stdout|stderr)\s+[FEB]?\s*(?P<message>.*)$"
)


def _level_from_message(message: str) -> LogLevel:
    """Heuristic: elevate level if message contains error/warning keywords."""
    lower = (message or "").lower()
    if any(k in lower for k in ("error", "err", "critical", "fatal", "failed", "exception")):
        return LogLevel.ERROR
    if any(k in lower for k in ("warn", "warning")):
        return LogLevel.WARNING
    return LogLevel.INFO


class DockerParser(BaseLogParser):
    """Parser for Docker container logs (JSON or raw timestamped format)."""

    @property
    def source_name(self) -> str:
        return "docker"

    def can_handle(self, line: str) -> bool:
        stripped = line.strip()
        if not stripped:
            return False
        if stripped.startswith("{"):
            try:
                obj = json.loads(stripped)
                return isinstance(obj, dict) and ("log" in obj or "message" in obj)
            except json.JSONDecodeError:
                pass
        if DOCKER_RAW_LINE.match(stripped):
            return True
        # Plain line with Docker-style ISO timestamp at start
        if re.match(r"^\d{4}-\d{2}-\d{2}T[\d.:]+Z\s", stripped):
            return True
        return False

    def _parse_iso_timestamp(self, s: str) -> datetime | None:
        try:
            # Trim fractional seconds to 6 digits for strptime
            s = re.sub(r"(\.\d{6})\d*Z$", r"\1Z", s)
            if s.endswith("Z"):
                s = s[:-1] + "+00:00"
            return datetime.fromisoformat(s)
        except (ValueError, TypeError):
            return None

    def parse(self, lines: list[str]) -> list[LogEvent]:
        events: list[LogEvent] = []
        for raw in lines:
            line = raw.strip()
            if not line:
                continue
            # JSON format
            if line.startswith("{"):
                try:
                    obj = json.loads(line)
                    if not isinstance(obj, dict):
                        continue
                    msg = obj.get("log") or obj.get("message") or ""
                    if isinstance(msg, bytes):
                        msg = msg.decode("utf-8", errors="replace")
                    msg = msg.strip().strip("\n")
                    stream = obj.get("stream", "stdout")
                    time_str = obj.get("time")
                    ts = None
                    if time_str and isinstance(time_str, str):
                        ts = self._parse_iso_timestamp(time_str)
                    level = LogLevel.ERROR if stream == "stderr" else _level_from_message(msg)
                    events.append(
                        LogEvent(
                            timestamp=ts,
                            level=level,
                            message=msg or raw,
                            source=self.source_name,
                            raw=raw,
                        )
                    )
                except json.JSONDecodeError:
                    events.append(
                        LogEvent(
                            timestamp=None,
                            level=LogLevel.INFO,
                            message=line,
                            source=self.source_name,
                            raw=raw,
                        )
                    )
                continue
            # Raw Docker format: timestamp stream F message
            m = DOCKER_RAW_LINE.match(line)
            if m:
                ts = self._parse_iso_timestamp(m.group("timestamp"))
                msg = m.group("message").strip()
                stream = m.group("stream")
                level = LogLevel.ERROR if stream == "stderr" else _level_from_message(msg)
                events.append(
                    LogEvent(
                        timestamp=ts,
                        level=level,
                        message=msg or line,
                        source=self.source_name,
                        raw=raw,
                    )
                )
                continue
            # Plain line with leading ISO timestamp
            if re.match(r"^\d{4}-\d{2}-\d{2}T[\d.:]+Z\s", line):
                parts = line.split(None, 1)
                ts = self._parse_iso_timestamp(parts[0]) if len(parts) > 0 else None
                msg = parts[1] if len(parts) > 1 else line
                events.append(
                    LogEvent(
                        timestamp=ts,
                        level=_level_from_message(msg),
                        message=msg.strip(),
                        source=self.source_name,
                        raw=raw,
                    )
                )
                continue
            # Fallback: treat as single message (e.g. plain container output)
            events.append(
                LogEvent(
                    timestamp=None,
                    level=_level_from_message(line),
                    message=line,
                    source=self.source_name,
                    raw=raw,
                )
            )
        return events
