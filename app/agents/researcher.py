from app.core.state import AgentState
from app.mcp.client import create_research_client
from app.mcp.client import (
    create_research_client,
    extract_tool_result,
)


class ResearchAgent:
    """
    Agent responsible for researching external market factors
    through the Research MCP server.
    """

    name = "research_agent"

    async def run(self, state: AgentState) -> AgentState:
        """
        Perform research based on the current workflow task
        and update the shared state.
        """

        state.status = "research_in_progress"

        # For the MVP, use a controlled research topic.
        topic = "general market factors"

        try:
            async with create_research_client() as client:

                raw_result = await client.call_tool(
                    "research_topic",
                    {
                        "topic": topic
                    },
                )
                result = extract_tool_result(raw_result)

            state.research_results = {
                "topic": topic,
                "result": result,
            }

            state.status = "research_completed"

        except Exception as exc:
            state.status = "research_failed"
            state.errors.append(
                f"{self.name}: {str(exc)}"
            )

        return state