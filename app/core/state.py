from typing import Any
from pydantic import BaseModel, Field


class AgentState(BaseModel):
    """
    Shared state passed between agents during a workflow.
    """

    task: str

    status: str = "initialized"

    data_analysis: dict[str, Any] | None = None

    research_results: dict[str, Any] | None = None

    report: dict[str, Any] | None = None

    validation: dict[str, Any] | None = None

    errors: list[str] = Field(default_factory=list)