from fastapi import APIRouter

from app.agents.orchestrator import OrchestratorAgent
from app.models.schemas import (
    WorkflowRequest,
    WorkflowResponse,
)


router = APIRouter(
    prefix="/api/v1",
    tags=["Workflows"],
)


@router.post(
    "/workflows",
    response_model=WorkflowResponse,
)
async def execute_workflow(
    request: WorkflowRequest,
):

    orchestrator = OrchestratorAgent()

    state = await orchestrator.run(
        request.task
    )

    return WorkflowResponse(
        status=state.status,
        task=state.task,
        validation=state.validation,
        errors=state.errors,
        report=state.report,
    )