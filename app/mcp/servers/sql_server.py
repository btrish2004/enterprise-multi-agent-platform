import sys
from pathlib import Path

# Add project root to Python path so this file can be
# executed directly by MCP Inspector.
PROJECT_ROOT = Path(__file__).resolve().parents[3]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from mcp.server import MCPServer

from app.core.database import get_connection


mcp = MCPServer(
    "Enterprise SQL Server",
    instructions="Provides read-only access to the enterprise sales database.",
)


@mcp.tool()
def execute_sql(query: str) -> list[dict]:
    """
    Execute a read-only SQL query against the enterprise sales database.

    Only SELECT queries are allowed.
    """

    normalized_query = query.strip().lower()

    if not normalized_query.startswith("select"):
        raise ValueError("Only SELECT queries are allowed.")

    connection = get_connection()

    try:
        cursor = connection.cursor()
        cursor.execute(query)

        rows = cursor.fetchall()

        return [dict(row) for row in rows]

    finally:
        connection.close()


if __name__ == "__main__":
    mcp.run()