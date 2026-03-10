from pydantic import BaseModel, Field

from app.models.log_event import LogEvent


class SuggestedFix(BaseModel):
    cause: str = Field(description="Root cause this fix addresses")
    fix: str = Field(description="Suggested remediation step(s)")


class AnalysisResult(BaseModel):
    errors: list[LogEvent] = Field(default_factory=list, description="Extracted error log events")
    warnings: list[LogEvent] = Field(default_factory=list, description="Extracted warning log events")
    root_causes: list[str] = Field(default_factory=list, description="Suspected root causes")
    suggested_fixes: list[SuggestedFix] = Field(
        default_factory=list,
        description="Suggested fixes per root cause",
    )
    summary: str | None = Field(default=None, description="Optional brief summary")
