from app.services.planner import PlannerService
import pytest

def test_planner_builds_safe_workflow(
    monkeypatch,
):

    fake_response = """
    {
        "reasoning": "Sales analysis and market research are required.",
        "agents": [
            "data_analyst",
            "research_agent",
            "report_agent"
        ]
    }
    """

    def fake_generate(prompt):
        return fake_response

    monkeypatch.setattr(
        "app.services.planner.local_llm.generate",
        fake_generate,
    )

    planner = PlannerService()

    plan = planner.create_plan(
        """
        Analyze Q3 sales performance,
        research market factors,
        and prepare a report.
        """
    )

    agents = [
        task.agent
        for task in plan.tasks
    ]

    assert agents == [
        "data_analyst",
        "research_agent",
        "report_agent",
        "validator_agent",
    ]

    report_task = next(
        task
        for task in plan.tasks
        if task.agent == "report_agent"
    )

    assert report_task.depends_on == [
        "data_analyst",
        "research_agent",
    ]

    validator_task = next(
        task
        for task in plan.tasks
        if task.agent == "validator_agent"
    )

    assert validator_task.depends_on == [
        "report_agent"
    ]


from app.models.schemas import (
    AgentTask,
    TaskPlan,
)
from app.services.planner import PlannerService


def test_planner_rejects_self_dependency():

    planner = PlannerService()

    invalid_plan = TaskPlan(
        reasoning="Invalid plan",
        tasks=[
            AgentTask(
                agent="data_analyst",
                objective="Analyze data",
                depends_on=[
                    "data_analyst"
                ],
            )
        ],
    )

    with pytest.raises(ValueError):

        planner._validate_agents(
            invalid_plan
        )