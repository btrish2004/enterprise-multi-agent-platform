import json
import re

from app.models.schemas import AgentTask, TaskPlan
from app.services.local_llm import local_llm


ALLOWED_AGENTS = {
    "data_analyst",
    "research_agent",
    "report_agent",
    "validator_agent",
}


class PlannerService:

    def _extract_json(self, response: str) -> dict:
        """
        Extract JSON from the LLM response.
        Handles plain JSON and JSON inside markdown fences.
        """

        response = response.strip()

        response = re.sub(
            r"```json\s*",
            "",
            response,
            flags=re.IGNORECASE,
        )

        response = re.sub(
            r"```\s*$",
            "",
            response,
        )

        start = response.find("{")
        end = response.rfind("}")

        if start == -1 or end == -1:
            raise ValueError(
                "LLM response does not contain valid JSON."
            )

        json_text = response[start:end + 1]

        return json.loads(json_text)

    def _validate_agents(
        self,
        plan: TaskPlan,
    ) -> TaskPlan:
        """
        Validate the agent names and dependency references
        produced by the planner.
        """

        # -------------------------------------------------
        # Validate agent names and dependencies
        # -------------------------------------------------

        for task in plan.tasks:

            if task.agent not in ALLOWED_AGENTS:
                raise ValueError(
                    f"Unknown agent selected by planner: "
                    f"{task.agent}"
                )

            for dependency in task.depends_on:

                if dependency not in ALLOWED_AGENTS:
                    raise ValueError(
                        f"Unknown dependency: "
                        f"{dependency}"
                    )

                if dependency == task.agent:
                    raise ValueError(
                        f"Agent '{task.agent}' "
                        f"cannot depend on itself."
                    )

        # -------------------------------------------------
        # Validate that dependencies exist in the plan
        # -------------------------------------------------

        agent_names = {
            task.agent
            for task in plan.tasks
        }

        for task in plan.tasks:

            for dependency in task.depends_on:

                if dependency not in agent_names:
                    raise ValueError(
                        f"Agent '{task.agent}' depends on "
                        f"'{dependency}', but that agent "
                        f"is missing from the plan."
                    )

        # -------------------------------------------------
        # Detect circular dependencies
        # -------------------------------------------------

        dependency_map = {
            task.agent: task.depends_on
            for task in plan.tasks
        }

        def visit(
            agent: str,
            visiting: set[str],
            visited: set[str],
        ):

            if agent in visiting:
                raise ValueError(
                    "Circular dependency detected involving "
                    f"agent '{agent}'."
                )

            if agent in visited:
                return

            visiting.add(agent)

            for dependency in dependency_map.get(
                agent,
                [],
            ):
                visit(
                    dependency,
                    visiting,
                    visited,
                )

            visiting.remove(agent)
            visited.add(agent)

        visited = set()

        for agent in dependency_map:

            visit(
                agent,
                set(),
                visited,
            )

        return plan

    def create_plan(
        self,
        user_request: str,
    ) -> TaskPlan:
        """
        Use the local LLM to identify which agents are
        required for the user's request.

        Dependency relationships are constructed by the
        application rather than trusted to the LLM.
        """

        prompt = f"""
You are an enterprise workflow planner.

Your job is to identify which specialized agents
are required for the user's request.

Available agents:

data_analyst:
Analyzes sales, revenue, units, and enterprise
database data.

research_agent:
Researches market and external business factors.

report_agent:
Combines analysis and research into a business report.

validator_agent:
Validates completed workflow output.

User request:
{user_request}

Return ONLY valid JSON.

Use this exact format:

{{
  "reasoning": "short explanation",
  "agents": [
    "data_analyst",
    "research_agent",
    "report_agent"
  ]
}}

Rules:

- Only use the available agent names.
- Include data_analyst when the request requires
  sales, revenue, units, numerical, or database analysis.
- Include research_agent when the request requires
  market research or external business factors.
- Include report_agent when the user requests a
  report, summary, recommendations, or combined result.
- Do not include validator_agent. The platform will
  add validation automatically.
- Do not create dependencies.
- Do not return markdown.
- Return only the JSON object.
"""

        response = local_llm.generate(prompt)

        print("\nRaw planner response:")
        print(response)

        data = self._extract_json(response)

        # -------------------------------------------------
        # Read the agents selected by the LLM
        # -------------------------------------------------

        selected_agents = data.get(
            "agents",
            [],
        )

        if not isinstance(
            selected_agents,
            list,
        ):
            raise ValueError(
                "Planner 'agents' field must be a list."
            )

        # -------------------------------------------------
        # Validate the selected agent names
        # -------------------------------------------------

        for agent_name in selected_agents:

            if agent_name not in ALLOWED_AGENTS:

                raise ValueError(
                    f"Unknown agent selected by planner: "
                    f"{agent_name}"
                )

        # Remove duplicates while preserving order.
        selected_agents = list(
            dict.fromkeys(selected_agents)
        )

        # -------------------------------------------------
        # Build the workflow deterministically
        # -------------------------------------------------

        task_map = {}

        if "data_analyst" in selected_agents:

            task_map["data_analyst"] = AgentTask(
                agent="data_analyst",
                objective=(
                    "Analyze the relevant enterprise "
                    "sales and numerical data."
                ),
                depends_on=[],
            )

        if "research_agent" in selected_agents:

            research_dependencies = []

            # Research can use the data analysis to
            # investigate the factors behind the results.
            if "data_analyst" in task_map:

                research_dependencies.append(
                    "data_analyst"
                )

            task_map["research_agent"] = AgentTask(
                agent="research_agent",
                objective=(
                    "Research relevant market and "
                    "external business factors."
                ),
                depends_on=research_dependencies,
            )

        if "report_agent" in selected_agents:

            report_dependencies = []

            if "data_analyst" in task_map:

                report_dependencies.append(
                    "data_analyst"
                )

            if "research_agent" in task_map:

                report_dependencies.append(
                    "research_agent"
                )

            task_map["report_agent"] = AgentTask(
                agent="report_agent",
                objective=(
                    "Combine the available analysis and "
                    "research into a business report."
                ),
                depends_on=report_dependencies,
            )

        # -------------------------------------------------
        # Validation is mandatory when a report exists.
        # -------------------------------------------------

        if "report_agent" in task_map:

            task_map["validator_agent"] = AgentTask(
                agent="validator_agent",
                objective=(
                    "Validate the completed workflow output."
                ),
                depends_on=[
                    "report_agent"
                ],
            )

        # -------------------------------------------------
        # If no report was requested but other work exists,
        # still validate the workflow output.
        # -------------------------------------------------

        elif task_map:

            last_agent = None

            if "research_agent" in task_map:

                last_agent = "research_agent"

            elif "data_analyst" in task_map:

                last_agent = "data_analyst"

            if last_agent:

                task_map["validator_agent"] = AgentTask(
                    agent="validator_agent",
                    objective=(
                        "Validate the completed "
                        "workflow output."
                    ),
                    depends_on=[
                        last_agent
                    ],
                )

        # -------------------------------------------------
        # Return tasks in deterministic execution order.
        # -------------------------------------------------

        ordered_agents = [
            "data_analyst",
            "research_agent",
            "report_agent",
            "validator_agent",
        ]

        ordered_tasks = [
            task_map[agent]
            for agent in ordered_agents
            if agent in task_map
        ]

        plan = TaskPlan(
            reasoning=data.get(
                "reasoning",
                "Workflow generated by the local planner.",
            ),
            tasks=ordered_tasks,
        )

        # -------------------------------------------------
        # Final safety validation
        # -------------------------------------------------

        return self._validate_agents(plan)


planner_service = PlannerService()