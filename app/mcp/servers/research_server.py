import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from mcp.server import MCPServer


mcp = MCPServer(
    "Enterprise Research Server",
    instructions=(
        "Provides controlled research capabilities for enterprise analysis."
    ),
)


@mcp.tool()
def research_topic(topic: str) -> dict:
    """
    Research an enterprise topic and return structured findings.

    This initial MVP implementation uses controlled sample research data.
    """

    research_data = {
        "beverage_market": {
            "topic": "Beverage market",
            "factors": [
                "Changing consumer preferences",
                "Competitive pricing",
                "Seasonal demand",
                "Distribution availability",
            ],
        },
        "snacks_market": {
            "topic": "Snacks market",
            "factors": [
                "Consumer demand changes",
                "Promotional activity",
                "Competitive products",
                "Regional pricing differences",
            ],
        },
        "general_market": {
            "topic": "General market factors",
            "factors": [
                "Consumer demand",
                "Competitive activity",
                "Pricing changes",
                "Distribution changes",
                "Seasonality",
            ],
        },
    }

    normalized_topic = topic.lower().strip()

    if "beverage" in normalized_topic:
        return research_data["beverage_market"]

    if "snack" in normalized_topic:
        return research_data["snacks_market"]

    return research_data["general_market"]


if __name__ == "__main__":
    mcp.run()