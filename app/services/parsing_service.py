from app.models.log_event import LogEvent
from app.parsers import NginxParser, SyslogParser
from app.parsers.base_parser import BaseLogParser

_PARSERS: list[BaseLogParser] = [NginxParser(), SyslogParser()]


def parse(content: str, filename: str | None = None, parser_hint: str | None = None) -> list[LogEvent]:
    """
    Parse log content into a list of LogEvent.
    If parser_hint is given ('nginx' or 'syslog'), use that parser; else auto-detect from first lines.
    """
    lines = content.splitlines()
    if not lines:
        return []

    parser: BaseLogParser | None = None
    if parser_hint:
        hint_lower = parser_hint.lower()
        for p in _PARSERS:
            if p.source_name == hint_lower:
                parser = p
                break

    if parser is None:
        for p in _PARSERS:
            for line in lines[:5]:
                if line.strip() and p.can_handle(line):
                    parser = p
                    break
            if parser is not None:
                break

    if parser is None:
        parser = SyslogParser()

    return parser.parse(lines)
