import pytest

from app.agents.orchestrator import OrchestratorAgent
from app.models.schemas import AgentTask, TaskPlan
from app.services.planner import planner_service


@pytest.mark.asyncio
async def test_end_to_end_workflow(monkeypatch):

    monkeypatch.setattr(
        planner_service,
        "create_plan",
        lambda task: TaskPlan(
            reasoning="Test workflow plan",
            tasks=[
                AgentTask(
                    agent="data_analyst",
                    objective="Analyze sales data",
                    depends_on=[],
                ),
                AgentTask(
                    agent="research_agent",
                    objective="Research market factors",
                    depends_on=["data_analyst"],
                ),
                AgentTask(
                    agent="report_agent",
                    objective="Generate report",
                    depends_on=[
                        "data_analyst",
                        "research_agent",
                    ],
                ),
                AgentTask(
                    agent="validator_agent",
                    objective="Validate workflow",
                    depends_on=["report_agent"],
                ),
            ],
        ),
    )

    orchestrator = OrchestratorAgent()

    state = await orchestrator.run(
        "Analyze Q3 sales performance."
    )

    assert state.status == "workflow_completed"

    assert state.validation is not None
    assert state.validation["status"] == "passed"

    assert state.errors == []

    assert state.data_analysis is not None

    assert state.data_analysis["declining_regions"] == [
        "West",
        "South",
    ]

    assert state.report is not None

    assert (
        state.report["title"]
        == "Q3 Sales Performance Analysis"
    )

    assert (
        state.report["sales_analysis"][
            "declining_regions"
        ]
        == ["West", "South"]
    )

    assert (
        len(
            state.report["sales_analysis"][
                "declining_region_details"
            ]
        )
        == 2
    )

    assert state.report["artifact"] is not None

    assert (
        state.report["artifact"]["status"]
        == "created"
    )

    assert (
        state.report["artifact"]["filename"]
        == "q3_sales_performance.md"
    )