from pydantic import BaseModel, Field


class AgentTask(BaseModel):
    agent: str
    objective: str
    depends_on: list[str] = Field(default_factory=list)


class TaskPlan(BaseModel):
    reasoning: str
    tasks: list[AgentTask]


class WorkflowRequest(BaseModel):
    task: str


class WorkflowResponse(BaseModel):
    status: str
    task: str
    validation: dict | None = None
    errors: list[str] = Field(default_factory=list)
    report: dict | None = None