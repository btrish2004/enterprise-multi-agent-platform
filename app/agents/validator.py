from app.core.state import AgentState


class ValidatorAgent:
    """
    Validates the outputs produced by the other agents.
    """

    name = "validator_agent"

    async def run(self, state: AgentState) -> AgentState:
        """
        Validate the current workflow state.
        """

        state.status = "validation_in_progress"

        validation_errors = []

        # Validate data analysis
        if state.data_analysis is None:
            validation_errors.append(
                "Data analysis results are missing."
            )

        # Validate research
        if state.research_results is None:
            validation_errors.append(
                "Research results are missing."
            )

        # Validate report
        if state.report is None:
            validation_errors.append(
                "Report is missing."
            )

        # Validate report structure
        if state.report is not None:

            required_fields = [
                "title",
                "summary",
                "sales_analysis",
                "market_research",
                "recommendations",
            ]

            for field in required_fields:
                if field not in state.report:
                    validation_errors.append(
                        f"Report field '{field}' is missing."
                    )

        # Validate workflow errors
        if state.errors:
            validation_errors.extend(
                state.errors
            )

        if validation_errors:

            state.validation = {
                "status": "failed",
                "errors": validation_errors,
            }

            state.status = "validation_failed"

        else:

            state.validation = {
                "status": "passed",
                "errors": [],
            }

            state.status = "validation_passed"

        return state