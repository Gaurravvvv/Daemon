from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router as api_router
from contextlib import asynccontextmanager
import asyncio
from services.database import connect_to_mongo, close_mongo_connection
from core.aggregator import monitor_jobs

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await connect_to_mongo()
    # Spawn the background aggregator loop
    app.state.aggregator_task = asyncio.create_task(monitor_jobs())
    yield
    # Shutdown
    await close_mongo_connection()

app = FastAPI(
    title="DaeMon Grid Orchestrator",
    description="Master orchestrator for distributed compute grid",
    version="1.0.0",
    lifespan=lifespan
)

# CORS config to allow the React dashboard to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register our REST API endpoints
app.include_router(api_router)

@app.get("/")
async def root():
    return {"status": "online", "service": "daemon-orchestrator"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
