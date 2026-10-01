from app.core.state import AgentState
from app.mcp.client import (
    create_file_client,
    extract_tool_result,
)


class ReportAgent:
    name = "report_agent"

    async def run(
        self,
        state: AgentState,
    ) -> AgentState:

        state.status = (
            "report_generation_in_progress"
        )

        try:

            if state.data_analysis is None:
                raise ValueError(
                    "Data analysis results are missing."
                )

            if state.research_results is None:
                raise ValueError(
                    "Research results are missing."
                )

            regional_analysis = (
                state.data_analysis.get(
                    "regional_analysis",
                    [],
                )
            )

            declining_regions = (
                state.data_analysis.get(
                    "declining_regions",
                    [],
                )
            )

            declining_details = []

            for region_data in regional_analysis:

                if (
                    region_data["trend"]
                    == "Declining"
                ):
                    declining_details.append(
                        {
                            "region": region_data["region"],
                            "q2_revenue": region_data[
                                "q2_revenue"
                            ],
                            "q3_revenue": region_data[
                                "q3_revenue"
                            ],
                            "change": region_data[
                                "q3_vs_q2"
                            ],
                        }
                    )

            report = {
                "title": (
                    "Q3 Sales Performance Analysis"
                ),
                "summary": (
                    "The analysis identifies regional "
                    "sales trends by comparing Q3 "
                    "performance with Q2 and combines "
                    "the results with relevant market "
                    "factors."
                ),
                "sales_analysis": {
                    "regional_analysis": (
                        regional_analysis
                    ),
                    "declining_regions": (
                        declining_regions
                    ),
                    "declining_region_details": (
                        declining_details
                    ),
                },
                "market_research": (
                    state.research_results
                ),
                "recommendations": [
                    (
                        "Investigate the drivers of "
                        "declining sales in the "
                        "identified regions."
                    ),
                    (
                        "Review competitive activity "
                        "and pricing changes in "
                        "declining regions."
                    ),
                    (
                        "Evaluate distribution and "
                        "product availability in "
                        "declining regions."
                    ),
                    (
                        "Compare consumer demand and "
                        "seasonal effects across "
                        "regions."
                    ),
                ],
            }

            # -------------------------------------------------
            # Generate Markdown artifact
            # -------------------------------------------------

            markdown_report = (
                self._build_markdown_report(
                    report
                )
            )

            # -------------------------------------------------
            # Create report through File MCP
            # -------------------------------------------------

            async with create_file_client() as client:

                raw_result = await client.call_tool(
                    "create_report",
                    {
                        "filename": (
                            "q3_sales_performance.md"
                        ),
                        "content": markdown_report,
                    },
                )

                file_result = extract_tool_result(
                    raw_result
                )

            report["artifact"] = file_result

            state.report = report

            state.status = (
                "report_completed"
            )

        except Exception as exc:

            state.status = (
                "report_failed"
            )

            state.errors.append(
                f"{self.name}: {str(exc)}"
            )

        return state

    def _build_markdown_report(
        self,
        report: dict,
    ) -> str:

        lines = []

        # -------------------------------------------------
        # Title
        # -------------------------------------------------

        lines.append(
            f"# {report['title']}"
        )

        lines.append("")

        # -------------------------------------------------
        # Summary
        # -------------------------------------------------

        lines.append("## Summary")
        lines.append("")
        lines.append(
            report["summary"]
        )
        lines.append("")

        # -------------------------------------------------
        # Regional Performance
        # -------------------------------------------------

        lines.append(
            "## Regional Sales Performance"
        )

        lines.append("")

        lines.append(
            "| Region | Q1 Revenue | Q2 Revenue | "
            "Q3 Revenue | Q3 vs Q2 | Trend |"
        )

        lines.append(
            "|---|---:|---:|---:|---:|---|"
        )

        regional_analysis = (
            report["sales_analysis"][
                "regional_analysis"
            ]
        )

        for row in regional_analysis:

            change = row["q3_vs_q2"]

            if change >= 0:
                change_text = (
                    f"+{change:,.0f}"
                )
            else:
                change_text = (
                    f"{change:,.0f}"
                )

            lines.append(
                f"| {row['region']} "
                f"| {row['q1_revenue']:,.0f} "
                f"| {row['q2_revenue']:,.0f} "
                f"| {row['q3_revenue']:,.0f} "
                f"| {change_text} "
                f"| {row['trend']} |"
            )

        lines.append("")

        # -------------------------------------------------
        # Declining Regions
        # -------------------------------------------------

        lines.append(
            "## Declining Regions"
        )

        lines.append("")

        declining_details = (
            report["sales_analysis"][
                "declining_region_details"
            ]
        )

        if declining_details:

            for item in declining_details:

                lines.append(
                    f"- **{item['region']}**: "
                    f"Q3 revenue decreased by "
                    f"{abs(item['change']):,.0f} "
                    f"from Q2."
                )

        else:

            lines.append(
                "No declining regions were identified."
            )

        lines.append("")

        # -------------------------------------------------
        # Market Factors
        # -------------------------------------------------

        lines.append(
            "## Market Factors"
        )

        lines.append("")

        research_result = (
            report["market_research"][
                "result"
            ]
        )

        if isinstance(
            research_result,
            dict,
        ):

            factors = research_result.get(
                "factors",
                [],
            )

            for factor in factors:

                lines.append(
                    f"- {factor}"
                )

        else:

            lines.append(
                str(research_result)
            )

        lines.append("")

        # -------------------------------------------------
        # Recommendations
        # -------------------------------------------------

        lines.append(
            "## Recommendations"
        )

        lines.append("")

        for recommendation in report[
            "recommendations"
        ]:

            lines.append(
                f"- {recommendation}"
            )

        lines.append("")

        return "\n".join(lines)