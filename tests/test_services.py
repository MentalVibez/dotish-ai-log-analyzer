from unittest.mock import patch

import pytest

from app.models.log_event import LogEvent, LogLevel
from app.models.analysis_result import AnalysisResult, SuggestedFix
from app.services.parsing_service import parse
from app.services.analysis_service import analyze
from app.services.report_service import format_for_api


class TestParsingService:
    def test_parse_nginx_content(self):
        content = """2024/01/15 12:00:00 [error] 1#0: test error
2024/01/15 12:00:01 [warn] 1#0: test warn
"""
        events = parse(content)
        assert len(events) >= 2
        levels = [e.level for e in events]
        assert LogLevel.ERROR in levels
        assert LogLevel.WARNING in levels

    def test_parse_with_hint(self):
        content = "Jan 15 12:00:00 host app: message"
        events = parse(content, parser_hint="syslog")
        assert len(events) == 1
        assert events[0].source == "syslog"


class TestReportService:
    def test_format_for_api(self):
        result = AnalysisResult(
            errors=[LogEvent(level=LogLevel.ERROR, message="e1", source="nginx", raw="e1")],
            warnings=[],
            root_causes=["cause1"],
            suggested_fixes=[SuggestedFix(cause="cause1", fix="do X")],
        )
        out = format_for_api(result)
        assert "errors" in out
        assert len(out["errors"]) == 1
        assert out["root_causes"] == ["cause1"]
        assert len(out["suggested_fixes"]) == 1
        assert out["suggested_fixes"][0]["fix"] == "do X"


class TestAnalysisService:
    @pytest.mark.skip(reason="Requires Ollama; run integration tests manually")
    def test_analyze_integration(self):
        content = "2024/01/15 12:00:00 [error] 1#0: connection refused"
        result = analyze(content)
        assert isinstance(result, AnalysisResult)
        assert hasattr(result, "errors")
        assert hasattr(result, "root_causes")
        assert hasattr(result, "suggested_fixes")

    @patch("app.services.analysis_service.run_full_analysis")
    def test_analyze_mocked_llm(self, mock_run):
        mock_run.return_value = AnalysisResult(
            errors=[],
            warnings=[],
            root_causes=["Network issue"],
            suggested_fixes=[SuggestedFix(cause="Network issue", fix="Check firewall")],
        )
        result = analyze("some log line")
        assert result.root_causes == ["Network issue"]
        assert len(result.suggested_fixes) == 1
        mock_run.assert_called_once()
