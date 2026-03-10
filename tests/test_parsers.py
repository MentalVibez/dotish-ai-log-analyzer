from app.models.log_event import LogLevel
from app.parsers.nginx_parser import NginxParser
from app.parsers.syslog_parser import SyslogParser


class TestNginxParser:
    def test_can_handle_error_line(self):
        parser = NginxParser()
        line = "2024/01/15 12:00:00 [error] 1234#0: connect() failed"
        assert parser.can_handle(line) is True

    def test_parse_error_log(self):
        parser = NginxParser()
        lines = [
            "2024/01/15 12:00:00 [error] 1234#0: connect() failed",
            "2024/01/15 12:00:01 [warn] 1234#0: upstream timeout",
        ]
        events = parser.parse(lines)
        assert len(events) == 2
        assert events[0].level == LogLevel.ERROR
        assert "connect() failed" in events[0].message
        assert events[0].source == "nginx"
        assert events[1].level == LogLevel.WARNING
        assert "upstream timeout" in events[1].message

    def test_parse_access_log_5xx(self):
        parser = NginxParser()
        lines = [
            '127.0.0.1 - - [15/Jan/2024:12:00:00 +0000] "GET /api HTTP/1.1" 502 0 "-" "-"',
        ]
        events = parser.parse(lines)
        assert len(events) == 1
        assert events[0].level == LogLevel.ERROR
        assert "502" in events[0].message

    def test_parse_access_log_4xx(self):
        parser = NginxParser()
        lines = [
            '127.0.0.1 - - [15/Jan/2024:12:00:00 +0000] "GET /missing HTTP/1.1" 404 0 "-" "-"',
        ]
        events = parser.parse(lines)
        assert len(events) == 1
        assert events[0].level == LogLevel.WARNING


class TestSyslogParser:
    def test_can_handle_rfc5424(self):
        parser = SyslogParser()
        line = "<34>1 2024-01-15T12:00:00Z host app 1 2 - message"
        assert parser.can_handle(line) is True

    def test_parse_bsd(self):
        parser = SyslogParser()
        lines = [
            "Jan 15 12:00:00 host myapp: connection refused",
        ]
        events = parser.parse(lines)
        assert len(events) == 1
        assert events[0].source == "syslog"
        assert "connection refused" in events[0].message
        assert events[0].level == LogLevel.ERROR

    def test_parse_rfc5424(self):
        parser = SyslogParser()
        lines = [
            "<34>1 2024-01-15T12:00:00Z host app 1 2 - test message",
        ]
        events = parser.parse(lines)
        assert len(events) == 1
        assert events[0].message == "test message"
        assert events[0].source == "syslog"
