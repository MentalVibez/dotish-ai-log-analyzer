import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_health(client: TestClient):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_analyze_requires_file(client: TestClient):
    r = client.post("/api/analyze")
    assert r.status_code == 422  # no file


def test_analyze_accepts_log_file(client: TestClient):
    from unittest.mock import patch
    from app.models.analysis_result import AnalysisResult, SuggestedFix

    with patch("app.api.analysis.analyze") as mock_analyze:
        mock_analyze.return_value = AnalysisResult(
            errors=[],
            warnings=[],
            root_causes=["Test cause"],
            suggested_fixes=[SuggestedFix(cause="Test cause", fix="Test fix")],
        )
        files = {"file": ("test.log", b"2024/01/15 12:00:00 [error] 1#0: test\n", "text/plain")}
        r = client.post("/api/analyze", files=files)
    assert r.status_code == 200
    data = r.json()
    assert "errors" in data
    assert "warnings" in data
    assert "root_causes" in data
    assert "suggested_fixes" in data


def test_analysis_run_empty_content(client: TestClient):
    r = client.post("/api/analysis/run", json={"log_content": ""})
    assert r.status_code == 400


def test_analysis_run_with_content(client: TestClient):
    from unittest.mock import patch
    from app.models.analysis_result import AnalysisResult, SuggestedFix

    with patch("app.api.analysis.analyze") as mock_analyze:
        mock_analyze.return_value = AnalysisResult(
            errors=[],
            warnings=[],
            root_causes=["Connection refused"],
            suggested_fixes=[SuggestedFix(cause="Connection refused", fix="Check service")],
        )
        r = client.post(
            "/api/analysis/run",
            json={"log_content": "2024/01/15 12:00:00 [error] 1#0: connection refused\n"},
        )
    assert r.status_code == 200
    data = r.json()
    assert "errors" in data
    assert "suggested_fixes" in data


def test_upload_returns_parsed_events(client: TestClient):
    files = {"file": ("x.log", b"2024/01/15 12:00:00 [error] 1#0: test\n", "text/plain")}
    r = client.post("/api/logs/upload", files=files)
    assert r.status_code == 200
    data = r.json()
    assert "events" in data
    assert "count" in data
    assert data["count"] >= 1
    assert data["events"][0]["message"]
