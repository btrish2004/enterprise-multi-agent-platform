from app.agents.data_analyst import DataAnalystAgent
from app.agents.researcher import ResearchAgent
from app.agents.report_agent import ReportAgent
from app.agents.validator import ValidatorAgent
from app.core.state import AgentState
from app.models.schemas import TaskPlan
from app.services.planner import planner_service


class OrchestratorAgent:
    name = "orchestrator"

    def __init__(self):

        self.agents = {
            "data_analyst": DataAnalystAgent(),
            "research_agent": ResearchAgent(),
            "report_agent": ReportAgent(),
            "validator_agent": ValidatorAgent(),
        }

    async def run(self, task: str) -> AgentState:

        state = AgentState(
            task=task,
            status="workflow_started",
        )

        try:

            # -------------------------------------------------
            # STEP 1: Generate execution plan
            # -------------------------------------------------

            state.status = "planning"

            plan: TaskPlan = planner_service.create_plan(task)

            print("\nGenerated workflow plan:")
            print(plan.model_dump_json(indent=2))

            # -------------------------------------------------
            # STEP 2: Execute planned tasks
            # -------------------------------------------------

            completed_agents = set()

            for planned_task in plan.tasks:

                agent_name = planned_task.agent

                print(
                    f"\nExecuting agent: {agent_name}"
                )

                # ---------------------------------------------
                # Validate dependencies
                # ---------------------------------------------

                missing_dependencies = [
                    dependency
                    for dependency in planned_task.depends_on
                    if dependency not in completed_agents
                ]

                if missing_dependencies:

                    raise RuntimeError(
                        f"Agent '{agent_name}' has unmet "
                        f"dependencies: {missing_dependencies}"
                    )

                # ---------------------------------------------
                # Find agent
                # ---------------------------------------------

                agent = self.agents.get(agent_name)

                if agent is None:

                    raise RuntimeError(
                        f"Unknown agent: {agent_name}"
                    )

                # ---------------------------------------------
                # Execute agent
                # ---------------------------------------------

                state = await agent.run(state)

                # ---------------------------------------------
                # Check execution failure
                # ---------------------------------------------

                if state.status.endswith("_failed"):

                    return state

                completed_agents.add(agent_name)

                print(
                    f"Completed agent: {agent_name}"
                )

            # -------------------------------------------------
            # STEP 3: Final workflow status
            # -------------------------------------------------

            state.status = "workflow_completed"

            return state

        except Exception as exc:

            state.status = "workflow_failed"

            state.errors.append(
                f"{self.name}: {str(exc)}"
            )

            return state