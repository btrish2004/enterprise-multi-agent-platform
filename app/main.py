from fastapi import FastAPI

from app.api.routes import router


app = FastAPI(
    title="Enterprise Multi-Agent Operations Platform",
    version="0.1.0",
    description=(
        "Multi-agent enterprise task execution "
        "platform using MCP."
    ),
)


app.include_router(router)


@app.get("/health")
async def health_check():

    return {
        "status": "healthy",
        "service": "enterprise-multi-agent-platform",
    }