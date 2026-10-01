from app.core.state import AgentState
from app.mcp.client import (
    create_sql_client,
    extract_tool_result,
)


class DataAnalystAgent:
    name = "data_analyst"

    async def run(
        self,
        state: AgentState,
    ) -> AgentState:

        state.status = "data_analysis_in_progress"

        query = """
            SELECT
                region,

                SUM(
                    CASE
                        WHEN quarter = 'Q1'
                        THEN revenue
                        ELSE 0
                    END
                ) AS q1_revenue,

                SUM(
                    CASE
                        WHEN quarter = 'Q2'
                        THEN revenue
                        ELSE 0
                    END
                ) AS q2_revenue,

                SUM(
                    CASE
                        WHEN quarter = 'Q3'
                        THEN revenue
                        ELSE 0
                    END
                ) AS q3_revenue,

                SUM(
                    CASE
                        WHEN quarter = 'Q1'
                        THEN units_sold
                        ELSE 0
                    END
                ) AS q1_units,

                SUM(
                    CASE
                        WHEN quarter = 'Q2'
                        THEN units_sold
                        ELSE 0
                    END
                ) AS q2_units,

                SUM(
                    CASE
                        WHEN quarter = 'Q3'
                        THEN units_sold
                        ELSE 0
                    END
                ) AS q3_units

            FROM sales

            GROUP BY region

            ORDER BY q3_revenue DESC;
        """

        try:

            async with create_sql_client() as client:

                raw_result = await client.call_tool(
                    "execute_sql",
                    {
                        "query": query
                    },
                )

                result = extract_tool_result(
                    raw_result
                )

            # -------------------------------------------------
            # Calculate regional trends
            # -------------------------------------------------

            regional_analysis = []
            declining_regions = []

            for row in result:

                q1_revenue = float(
                    row["q1_revenue"]
                )

                q2_revenue = float(
                    row["q2_revenue"]
                )

                q3_revenue = float(
                    row["q3_revenue"]
                )

                q3_vs_q2 = (
                    q3_revenue - q2_revenue
                )

                if q3_vs_q2 < 0:
                    trend = "Declining"
                    declining_regions.append(
                        row["region"]
                    )
                elif q3_vs_q2 > 0:
                    trend = "Growing"
                else:
                    trend = "Stable"

                regional_analysis.append(
                    {
                        "region": row["region"],
                        "q1_revenue": q1_revenue,
                        "q2_revenue": q2_revenue,
                        "q3_revenue": q3_revenue,
                        "q3_vs_q2": q3_vs_q2,
                        "q1_units": row["q1_units"],
                        "q2_units": row["q2_units"],
                        "q3_units": row["q3_units"],
                        "trend": trend,
                    }
                )

            # -------------------------------------------------
            # Store structured analysis in shared state
            # -------------------------------------------------

            state.data_analysis = {
                "analysis": (
                    "Quarterly regional sales "
                    "performance and trend analysis"
                ),
                "regional_analysis": regional_analysis,
                "declining_regions": declining_regions,
            }

            state.status = (
                "data_analysis_completed"
            )

        except Exception as exc:

            state.status = (
                "data_analysis_failed"
            )

            state.errors.append(
                f"{self.name}: {str(exc)}"
            )

        return state