import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from mcp.server import MCPServer


REPORTS_DIR = PROJECT_ROOT / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)


mcp = MCPServer(
    "Enterprise File Server",
    instructions=(
        "Provides controlled file operations for enterprise reports."
    ),
)


@mcp.tool()
def create_report(filename: str, content: str) -> dict:
    """
    Create a Markdown report inside the project's reports directory.

    Only Markdown files are allowed.
    """

    filename = filename.strip()

    if not filename.endswith(".md"):
        raise ValueError("Only Markdown (.md) files are allowed.")

    if "/" in filename or "\\" in filename or ".." in filename:
        raise ValueError("Invalid filename.")

    file_path = REPORTS_DIR / filename

    file_path.write_text(
        content,
        encoding="utf-8",
    )

    return {
        "status": "created",
        "filename": filename,
        "path": str(file_path),
    }


if __name__ == "__main__":
    mcp.run()